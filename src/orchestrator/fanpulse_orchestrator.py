"""
FanPulse Orchestrator - Main Orchestration Layer
Coordinates between VAR-Lens and Tactical Pulse agents
"""

import logging
import time
from typing import Dict, Any, Optional

from .query_router import QueryRouter, AgentType
from .response_handler import ResponseHandler
from src.agents.var_lens.rag_engine import VARLensRAG
from src.agents.tactical_pulse.match_analyzer import MatchAnalyzer

logger = logging.getLogger(__name__)


class FanPulseOrchestrator:
    """
    Main orchestrator for FanPulse system.
    
    Routes queries to appropriate agents and handles responses uniformly.
    Designed to work with LangFlow for visual workflow management.
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",
        model_name: str = "granite4.1:8b",
        data_path: str = "data/match_data/results.csv",
        vector_store_path: str = "data/vector_stores/var_lens_faiss"
    ):
        """
        Initialize the FanPulse orchestrator.
        
        Args:
            llm_provider: LLM provider for both routing and agents
            model_name: Model name for LLM
            data_path: Path to match data CSV
            vector_store_path: Path to VAR-Lens vector store
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.data_path = data_path
        self.vector_store_path = vector_store_path
        
        # Initialize components
        self.router = QueryRouter(llm_provider=llm_provider, model_name=model_name)
        self.response_handler = ResponseHandler()
        
        # Lazy initialization for agents (only when needed)
        self._var_lens = None
        self._tactical_pulse = None
        
        logger.info("FanPulse Orchestrator initialized")
    
    @property
    def var_lens(self) -> VARLensRAG:
        """Lazy initialization of VAR-Lens agent"""
        if self._var_lens is None:
            logger.info("Initializing VAR-Lens agent...")
            self._var_lens = VARLensRAG(
                vector_store_path=str(self.vector_store_path)
            )
            # Setup LLM for VAR-Lens
            self._var_lens.setup_llm(
                provider=self.llm_provider,
                model_name=self.model_name
            )
            logger.info("VAR-Lens agent initialized")
        return self._var_lens
    
    @property
    def tactical_pulse(self) -> MatchAnalyzer:
        """Lazy initialization of Tactical Pulse agent"""
        if self._tactical_pulse is None:
            logger.info("Initializing Tactical Pulse agent...")
            self._tactical_pulse = MatchAnalyzer(data_path=self.data_path)
            self._tactical_pulse.initialize_llm(
                provider=self.llm_provider,
                model_name=self.model_name
            )
            logger.info("Tactical Pulse agent initialized")
        return self._tactical_pulse
    
    def process_query(
        self,
        query: str,
        use_llm_routing: bool = True,
        force_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the orchestration pipeline.
        
        Args:
            query: User query string
            use_llm_routing: Whether to use LLM for intent classification
            force_agent: Force routing to specific agent ('var_lens' or 'tactical_pulse')
            
        Returns:
            Unified response dictionary
        """
        start_time = time.time()
        
        logger.info(f"Processing query: {query[:100]}...")
        
        try:
            # Route query to appropriate agent
            if force_agent:
                logger.info(f"Forcing routing to: {force_agent}")
                if force_agent == 'var_lens':
                    routing_result = {
                        'agent': AgentType.VAR_LENS,
                        'confidence': 'forced',
                        'method': 'manual',
                        'query': query
                    }
                elif force_agent == 'tactical_pulse':
                    routing_result = {
                        'agent': AgentType.TACTICAL_PULSE,
                        'confidence': 'forced',
                        'method': 'manual',
                        'query': query
                    }
                else:
                    raise ValueError(f"Invalid force_agent value: {force_agent}")
            else:
                routing_result = self.router.route_query(
                    query=query,
                    use_llm=use_llm_routing
                )
            
            # Log routing decision
            explanation = self.router.get_routing_explanation(routing_result)
            logger.info(f"Routing decision: {explanation}")
            
            # Execute query with appropriate agent
            agent_type = routing_result['agent']
            
            if agent_type == AgentType.VAR_LENS:
                agent_response = self._execute_var_lens_query(query)
            elif agent_type == AgentType.TACTICAL_PULSE:
                agent_response = self._execute_tactical_pulse_query(query)
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create unified response
            response = self.response_handler.create_unified_response(
                routing_result=routing_result,
                agent_response=agent_response,
                execution_time=execution_time
            )
            
            logger.info(f"Query processed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error processing query: {e}", exc_info=True)
            return self.response_handler.format_error_response(
                query=query,
                error_message=str(e),
                error_type=type(e).__name__
            )
    
    def _execute_var_lens_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a query with VAR-Lens agent.
        
        Args:
            query: User query
            
        Returns:
            VAR-Lens response dictionary
        """
        logger.info("Executing VAR-Lens query...")
        
        # Query the RAG system
        result = self.var_lens.query(query)
        
        # Extract sources from result
        sources = []
        if 'source_documents' in result:
            for doc in result['source_documents']:
                source_info = doc.metadata.get('source', 'Unknown')
                sources.append(source_info)
        
        return {
            'answer': result.get('result', 'No answer available'),
            'sources': sources,
            'metadata': result.get('metadata', {})
        }
    
    def _execute_tactical_pulse_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a query with Tactical Pulse agent.
        
        Args:
            query: User query
            
        Returns:
            Tactical Pulse response dictionary
        """
        logger.info("Executing Tactical Pulse query...")
        
        # Parse query to determine what type of analysis to perform
        query_lower = query.lower()
        
        # Check for match prediction keywords
        if any(word in query_lower for word in ['predict', 'prediction', 'vs', 'versus', 'against']):
            return self._handle_prediction_query(query)
        
        # Check for AI insights keywords
        elif any(word in query_lower for word in ['insight', 'analysis', 'tactical', 'performance']):
            return self._handle_insights_query(query)
        
        # Default to team analysis
        else:
            return self._handle_team_analysis_query(query)
    
    def _handle_prediction_query(self, query: str) -> Dict[str, Any]:
        """Handle match prediction queries"""
        # Extract team names from query (simplified - could be improved with NER)
        # For now, return a generic response structure
        logger.info("Handling prediction query")
        
        # This is a placeholder - in production, you'd extract team names
        # and call tactical_pulse.predict_match()
        return {
            'prediction': {
                'message': 'Match prediction requires team names. Please specify teams like "Brazil vs Argentina"'
            }
        }
    
    def _handle_insights_query(self, query: str) -> Dict[str, Any]:
        """Handle AI insights queries"""
        logger.info("Handling insights query")
        
        # Extract team name from query (simplified)
        # For now, return a generic response structure
        return {
            'ai_insights': {
                'message': 'AI insights require a team name. Please specify a team like "Brazil" or "Germany"'
            }
        }
    
    def _handle_team_analysis_query(self, query: str) -> Dict[str, Any]:
        """Handle team analysis queries"""
        logger.info("Handling team analysis query")
        
        # Extract team name from query (simplified)
        # For now, return a generic response structure
        return {
            'team_analysis': {
                'message': 'Team analysis requires a team name. Please specify a team like "Brazil" or "Argentina"'
            }
        }
    
    def process_var_lens_query(self, query: str) -> Dict[str, Any]:
        """
        Directly process a query with VAR-Lens (bypass routing).
        
        Args:
            query: User query
            
        Returns:
            Unified response dictionary
        """
        return self.process_query(query, force_agent='var_lens')
    
    def process_tactical_pulse_query(self, query: str) -> Dict[str, Any]:
        """
        Directly process a query with Tactical Pulse (bypass routing).
        
        Args:
            query: User query
            
        Returns:
            Unified response dictionary
        """
        return self.process_query(query, force_agent='tactical_pulse')
    
    def analyze_team(
        self,
        team_name: str,
        num_matches: int = 10,
        include_ai_insights: bool = False,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a specific team (convenience method).
        
        Args:
            team_name: Name of the team
            num_matches: Number of recent matches to analyze
            include_ai_insights: Whether to include AI-generated insights
            analysis_type: Type of AI analysis (comprehensive/tactical/performance)
            
        Returns:
            Unified response dictionary
        """
        logger.info(f"Analyzing team: {team_name}")
        
        start_time = time.time()
        
        try:
            # Get team analysis
            analysis = self.tactical_pulse.analyze_team(team_name, num_matches)
            
            # Add AI insights if requested
            if include_ai_insights:
                insights = self.tactical_pulse.generate_ai_insights(
                    team_name=team_name,
                    num_matches=num_matches,
                    analysis_type=analysis_type
                )
                analysis.update(insights)
            
            execution_time = time.time() - start_time
            
            # Create routing result for response formatting
            routing_result = {
                'agent': AgentType.TACTICAL_PULSE,
                'confidence': 'direct',
                'method': 'api',
                'query': f"Analyze {team_name}"
            }
            
            return self.response_handler.create_unified_response(
                routing_result=routing_result,
                agent_response=analysis,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing team: {e}", exc_info=True)
            return self.response_handler.format_error_response(
                query=f"Analyze {team_name}",
                error_message=str(e),
                error_type=type(e).__name__,
                agent='tactical_pulse'
            )
    
    def predict_match(
        self,
        home_team: str,
        away_team: str,
        num_matches: int = 10,
        include_ai_preview: bool = False
    ) -> Dict[str, Any]:
        """
        Predict a match outcome (convenience method).
        
        Args:
            home_team: Home team name
            away_team: Away team name
            num_matches: Number of recent matches to consider
            include_ai_preview: Whether to include AI-generated match preview
            
        Returns:
            Unified response dictionary
        """
        logger.info(f"Predicting match: {home_team} vs {away_team}")
        
        start_time = time.time()
        
        try:
            # Get match prediction
            prediction = self.tactical_pulse.predict_match(
                home_team=home_team,
                away_team=away_team
            )
            
            # Add AI preview if requested
            if include_ai_preview:
                preview = self.tactical_pulse.generate_match_preview(
                    home_team=home_team,
                    away_team=away_team,
                    num_matches=num_matches
                )
                prediction.update(preview)
            
            execution_time = time.time() - start_time
            
            # Create routing result for response formatting
            routing_result = {
                'agent': AgentType.TACTICAL_PULSE,
                'confidence': 'direct',
                'method': 'api',
                'query': f"Predict {home_team} vs {away_team}"
            }
            
            return self.response_handler.create_unified_response(
                routing_result=routing_result,
                agent_response=prediction,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error predicting match: {e}", exc_info=True)
            return self.response_handler.format_error_response(
                query=f"Predict {home_team} vs {away_team}",
                error_message=str(e),
                error_type=type(e).__name__,
                agent='tactical_pulse'
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status of all system components.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            'orchestrator': 'active',
            'router': 'active',
            'response_handler': 'active',
            'agents': {
                'var_lens': 'initialized' if self._var_lens else 'not_initialized',
                'tactical_pulse': 'initialized' if self._tactical_pulse else 'not_initialized'
            },
            'configuration': {
                'llm_provider': self.llm_provider,
                'model_name': self.model_name,
                'data_path': self.data_path,
                'vector_store_path': self.vector_store_path
            }
        }
        
        return status

# Made with Bob
