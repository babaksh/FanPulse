"""
Response Handler - Unified Response Formatting
Handles responses from both agents and formats them consistently
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses"""
    VAR_EXPLANATION = "var_explanation"
    TEAM_ANALYSIS = "team_analysis"
    MATCH_PREDICTION = "match_prediction"
    AI_INSIGHTS = "ai_insights"
    ERROR = "error"


class ResponseHandler:
    """
    Handles and formats responses from agents into a unified structure.
    
    Provides consistent response formatting regardless of which agent
    generated the response, making it easier to integrate with frontends
    and LangFlow workflows.
    """
    
    def __init__(self):
        """Initialize the response handler"""
        logger.info("Response Handler initialized")
    
    def format_var_lens_response(
        self,
        query: str,
        answer: str,
        sources: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a response from VAR-Lens agent.
        
        Args:
            query: Original user query
            answer: Answer from VAR-Lens
            sources: List of source documents used
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        response = {
            'type': ResponseType.VAR_EXPLANATION.value,
            'agent': 'var_lens',
            'query': query,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'sources': sources or [],
            'metadata': metadata or {}
        }
        
        logger.info(f"Formatted VAR-Lens response for query: {query[:50]}...")
        return response
    
    def format_tactical_pulse_response(
        self,
        query: str,
        analysis_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a response from Tactical Pulse agent.
        
        Args:
            query: Original user query
            analysis_type: Type of analysis (team_analysis, prediction, ai_insights)
            data: Analysis data from Tactical Pulse
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        # Determine response type based on analysis type
        if analysis_type == 'team_analysis':
            response_type = ResponseType.TEAM_ANALYSIS
        elif analysis_type == 'prediction':
            response_type = ResponseType.MATCH_PREDICTION
        elif analysis_type == 'ai_insights':
            response_type = ResponseType.AI_INSIGHTS
        else:
            response_type = ResponseType.TEAM_ANALYSIS
        
        response = {
            'type': response_type.value,
            'agent': 'tactical_pulse',
            'query': query,
            'analysis_type': analysis_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        logger.info(f"Formatted Tactical Pulse response ({analysis_type}) for query: {query[:50]}...")
        return response
    
    def format_error_response(
        self,
        query: str,
        error_message: str,
        error_type: str = "general",
        agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format an error response.
        
        Args:
            query: Original user query
            error_message: Error message
            error_type: Type of error
            agent: Agent that encountered the error (if applicable)
            
        Returns:
            Formatted error response dictionary
        """
        response = {
            'type': ResponseType.ERROR.value,
            'agent': agent or 'unknown',
            'query': query,
            'error': {
                'message': error_message,
                'type': error_type
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"Error response for query '{query[:50]}...': {error_message}")
        return response
    
    def create_unified_response(
        self,
        routing_result: Dict[str, Any],
        agent_response: Any,
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a unified response combining routing info and agent response.
        
        Args:
            routing_result: Result from QueryRouter.route_query()
            agent_response: Response from the agent
            execution_time: Time taken to execute the query (seconds)
            
        Returns:
            Unified response dictionary
        """
        from .query_router import AgentType
        
        agent_type = routing_result['agent']
        query = routing_result['query']
        
        # Add routing metadata
        metadata: Dict[str, Any] = {
            'routing': {
                'agent': agent_type.value,
                'confidence': routing_result['confidence'],
                'method': routing_result['method']
            }
        }
        
        if execution_time is not None:
            metadata['execution_time_seconds'] = execution_time
            metadata['execution_time_formatted'] = f"{execution_time:.2f}s"
        
        # Format based on agent type
        if agent_type == AgentType.VAR_LENS:
            if isinstance(agent_response, dict) and 'answer' in agent_response:
                return self.format_var_lens_response(
                    query=query,
                    answer=agent_response['answer'],
                    sources=agent_response.get('sources', []),
                    metadata=metadata
                )
            else:
                return self.format_error_response(
                    query=query,
                    error_message="Invalid VAR-Lens response format",
                    agent='var_lens'
                )
        
        elif agent_type == AgentType.TACTICAL_PULSE:
            if isinstance(agent_response, dict):
                # Determine analysis type from response
                analysis_type = 'team_analysis'
                if 'prediction' in agent_response:
                    analysis_type = 'prediction'
                elif 'ai_insights' in agent_response:
                    analysis_type = 'ai_insights'
                
                return self.format_tactical_pulse_response(
                    query=query,
                    analysis_type=analysis_type,
                    data=agent_response,
                    metadata=metadata
                )
            else:
                return self.format_error_response(
                    query=query,
                    error_message="Invalid Tactical Pulse response format",
                    agent='tactical_pulse'
                )
        
        else:
            return self.format_error_response(
                query=query,
                error_message="Unknown agent type",
                agent='unknown'
            )
    
    def format_for_display(self, response: Dict[str, Any]) -> str:
        """
        Format a response for human-readable display.
        
        Args:
            response: Response dictionary
            
        Returns:
            Formatted string for display
        """
        response_type = response.get('type', 'unknown')
        agent = response.get('agent', 'unknown')
        
        output = []
        output.append("=" * 70)
        output.append(f"FanPulse Response - {response_type.upper()}")
        output.append(f"Agent: {agent.upper()}")
        output.append("=" * 70)
        output.append("")
        
        # Add routing info if available
        if 'metadata' in response and 'routing' in response['metadata']:
            routing = response['metadata']['routing']
            output.append(f"Routing: {routing['method']} ({routing['confidence']} confidence)")
            output.append("")
        
        # Format based on response type
        if response_type == ResponseType.VAR_EXPLANATION.value:
            output.append(f"Query: {response['query']}")
            output.append("")
            output.append("Answer:")
            output.append(response['answer'])
            
            if response.get('sources'):
                output.append("")
                output.append("Sources:")
                for i, source in enumerate(response['sources'], 1):
                    output.append(f"  {i}. {source}")
        
        elif response_type in [ResponseType.TEAM_ANALYSIS.value, 
                               ResponseType.MATCH_PREDICTION.value,
                               ResponseType.AI_INSIGHTS.value]:
            output.append(f"Query: {response['query']}")
            output.append("")
            output.append(f"Analysis Type: {response['analysis_type']}")
            output.append("")
            output.append("Results:")
            
            # Format data based on type
            data = response.get('data', {})
            if 'ai_insights' in data:
                output.append(data['ai_insights'].get('content', 'No insights available'))
            else:
                # Generic data formatting
                for key, value in data.items():
                    if isinstance(value, dict):
                        output.append(f"\n{key.upper()}:")
                        for k, v in value.items():
                            output.append(f"  {k}: {v}")
                    else:
                        output.append(f"{key}: {value}")
        
        elif response_type == ResponseType.ERROR.value:
            output.append(f"Query: {response['query']}")
            output.append("")
            output.append("ERROR:")
            output.append(f"  Type: {response['error']['type']}")
            output.append(f"  Message: {response['error']['message']}")
        
        # Add execution time if available
        if 'metadata' in response and 'execution_time' in response['metadata']:
            output.append("")
            output.append(f"Execution Time: {response['metadata']['execution_time']}")
        
        output.append("")
        output.append("=" * 70)
        
        return "\n".join(output)
    
    def extract_key_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from a response for quick access.
        
        Args:
            response: Response dictionary
            
        Returns:
            Dictionary with key information
        """
        key_info = {
            'type': response.get('type'),
            'agent': response.get('agent'),
            'timestamp': response.get('timestamp')
        }
        
        response_type = response.get('type')
        
        if response_type == ResponseType.VAR_EXPLANATION.value:
            key_info['answer_preview'] = response.get('answer', '')[:200] + '...'
            key_info['num_sources'] = len(response.get('sources', []))
        
        elif response_type in [ResponseType.TEAM_ANALYSIS.value,
                               ResponseType.MATCH_PREDICTION.value,
                               ResponseType.AI_INSIGHTS.value]:
            key_info['analysis_type'] = response.get('analysis_type')
            data = response.get('data', {})
            
            # Extract key metrics
            if 'statistics' in data:
                key_info['win_rate'] = data['statistics'].get('win_rate')
            if 'prediction' in data:
                key_info['predicted_winner'] = data['prediction'].get('predicted_winner')
        
        elif response_type == ResponseType.ERROR.value:
            key_info['error_message'] = response['error']['message']
        
        return key_info

# Made with Bob
