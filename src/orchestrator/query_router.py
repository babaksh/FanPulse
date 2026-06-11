"""
Query Router - Intent Classification and Agent Selection
Routes user queries to the appropriate agent (VAR-Lens or Tactical Pulse)
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Available agent types"""
    VAR_LENS = "var_lens"
    TACTICAL_PULSE = "tactical_pulse"
    UNKNOWN = "unknown"


class QueryRouter:
    """
    Routes user queries to appropriate agents based on intent classification.
    
    Uses keyword matching and LLM-based classification to determine
    whether a query should go to VAR-Lens (rules/decisions) or
    Tactical Pulse (statistics/predictions).
    """
    
    def __init__(self, llm_provider: str = "ollama", model_name: str = "granite4.1:8b"):
        """
        Initialize the query router.
        
        Args:
            llm_provider: LLM provider to use for intent classification
            model_name: Model name for the LLM
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.llm = None
        
        # Keywords for VAR-Lens (rules, decisions, regulations)
        self.var_keywords = [
            'var', 'video assistant referee', 'referee', 'decision', 'rule',
            'offside', 'penalty', 'red card', 'yellow card', 'handball',
            'foul', 'regulation', 'law', 'fifa', 'ifab', 'protocol',
            'review', 'check', 'overturn', 'correct', 'incorrect'
        ]
        
        # Keywords for Tactical Pulse (statistics, predictions, analysis, tactical data)
        self.tactical_keywords = [
            'predict', 'prediction', 'forecast', 'odds', 'probability',
            'statistics', 'stats', 'performance', 'form', 'win rate',
            'goals', 'score', 'result', 'match', 'team', 'player',
            'analysis', 'analyze', 'compare', 'versus', 'vs',
            'head to head', 'h2h', 'history', 'record', 'trend',
            'tactical', 'strategy', 'formation', 'style', 'approach',
            'possession', 'shots', 'passes', 'passing', 'xg', 'expected goals',
            'defensive', 'attacking', 'defense', 'attack', 'counter',
            'pressing', 'build-up', 'transition', 'set piece', 'corner',
            'offside', 'discipline', 'cards', 'fouls', 'saves'
        ]
        
        logger.info("Query Router initialized")
    
    def _initialize_llm(self):
        """Initialize LLM for intent classification if not already initialized"""
        if self.llm is None:
            from src.agents.var_lens.llm_providers import LLMFactory
            self.llm = LLMFactory.create_llm(
                provider=self.llm_provider,
                model_name=self.model_name,
                temperature=0.3,  # Lower temperature for more consistent classification
                max_tokens=100
            )
            logger.info(f"LLM initialized for intent classification: {self.llm_provider}/{self.model_name}")
    
    def classify_intent_keyword(self, query: str) -> AgentType:
        """
        Classify query intent using keyword matching.
        
        Args:
            query: User query string
            
        Returns:
            AgentType indicating which agent should handle the query
        """
        query_lower = query.lower()
        
        # Count keyword matches
        var_matches = sum(1 for keyword in self.var_keywords if keyword in query_lower)
        tactical_matches = sum(1 for keyword in self.tactical_keywords if keyword in query_lower)
        
        logger.debug(f"Keyword matches - VAR: {var_matches}, Tactical: {tactical_matches}")
        
        # Determine agent based on keyword matches
        if var_matches > tactical_matches:
            return AgentType.VAR_LENS
        elif tactical_matches > var_matches:
            return AgentType.TACTICAL_PULSE
        else:
            return AgentType.UNKNOWN
    
    def classify_intent_llm(self, query: str) -> AgentType:
        """
        Classify query intent using LLM.
        
        Args:
            query: User query string
            
        Returns:
            AgentType indicating which agent should handle the query
        """
        self._initialize_llm()
        
        prompt = f"""Classify the following soccer/football query into one of these categories:

1. VAR_LENS - Questions about VAR decisions, referee rules, regulations, FIFA laws, offside rules, penalty decisions, card decisions, or any rule-related questions
2. TACTICAL_PULSE - Questions about team statistics, match predictions, performance analysis, tactical analysis, team comparisons, historical results, or player statistics

Query: "{query}"

Respond with ONLY one word: either "VAR_LENS" or "TACTICAL_PULSE"
"""
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            response_text = response_text.strip().upper()
            
            logger.debug(f"LLM classification response: {response_text}")
            
            if "VAR_LENS" in response_text:
                return AgentType.VAR_LENS
            elif "TACTICAL_PULSE" in response_text:
                return AgentType.TACTICAL_PULSE
            else:
                logger.warning(f"Unexpected LLM response: {response_text}")
                return AgentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Error in LLM classification: {e}")
            return AgentType.UNKNOWN
    
    def route_query(
        self,
        query: str,
        use_llm: bool = True,
        fallback_to_keyword: bool = True
    ) -> Dict[str, Any]:
        """
        Route a query to the appropriate agent.
        
        Args:
            query: User query string
            use_llm: Whether to use LLM for classification (default: True)
            fallback_to_keyword: Whether to fallback to keyword matching if LLM fails
            
        Returns:
            Dictionary containing:
                - agent: AgentType to handle the query
                - confidence: Confidence level (high/medium/low)
                - method: Classification method used (llm/keyword/default)
                - query: Original query
        """
        logger.info(f"Routing query: {query[:100]}...")
        
        # Try LLM classification first if enabled
        if use_llm:
            agent = self.classify_intent_llm(query)
            if agent != AgentType.UNKNOWN:
                logger.info(f"LLM classified query as: {agent.value}")
                return {
                    'agent': agent,
                    'confidence': 'high',
                    'method': 'llm',
                    'query': query
                }
        
        # Fallback to keyword matching
        if fallback_to_keyword or not use_llm:
            agent = self.classify_intent_keyword(query)
            if agent != AgentType.UNKNOWN:
                logger.info(f"Keyword matching classified query as: {agent.value}")
                return {
                    'agent': agent,
                    'confidence': 'medium',
                    'method': 'keyword',
                    'query': query
                }
        
        # Default to Tactical Pulse if uncertain
        logger.warning("Could not classify query, defaulting to Tactical Pulse")
        return {
            'agent': AgentType.TACTICAL_PULSE,
            'confidence': 'low',
            'method': 'default',
            'query': query
        }
    
    def get_routing_explanation(self, routing_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of the routing decision.
        
        Args:
            routing_result: Result from route_query()
            
        Returns:
            Explanation string
        """
        agent = routing_result['agent']
        confidence = routing_result['confidence']
        method = routing_result['method']
        
        agent_name = "VAR-Lens" if agent == AgentType.VAR_LENS else "Tactical Pulse"
        
        explanations = {
            'llm': f"AI classified this as a {agent_name} query with {confidence} confidence",
            'keyword': f"Keyword analysis suggests this is a {agent_name} query ({confidence} confidence)",
            'default': f"Defaulting to {agent_name} (unable to classify with certainty)"
        }
        
        return explanations.get(method, f"Routing to {agent_name}")

# Made with Bob
