"""
Reference Memory System for AlphaAxiom Learning Loop v2.0

This module implements a sophisticated reference memory system that stores
historical trading decisions with full contextual data, enabling the system
to learn from past experiences and make better decisions through similarity
search and pattern recognition.

The system combines:
1. Vector embeddings for semantic search
2. Metadata storage for precise filtering
3. Temporal indexing for time-based retrieval
4. Counterfactual analysis support
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TradingDecisionContext:
    """Full context of a trading decision"""
    symbol: str
    price_data: Dict[str, Any]
    technical_indicators: Dict[str, float]
    market_sentiment: Dict[str, Any]
    news_sentiment: Dict[str, Any]
    social_sentiment: Dict[str, Any]
    risk_metrics: Dict[str, float]
    timestamp: datetime
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingDecisionRecord:
    """A complete record of a trading decision and its outcome"""
    decision_id: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    context: TradingDecisionContext
    expected_outcome: float
    actual_outcome: float
    prediction_error: float
    was_correct: bool
    embedding: List[float]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimilarDecision:
    """A similar historical decision found through similarity search"""
    decision_id: str
    symbol: str
    action: str
    confidence: float
    similarity: float
    expected_outcome: float
    actual_outcome: float
    was_correct: bool
    context_summary: Dict[str, Any]
    timestamp: datetime


class ReferenceMemory:
    """
    Enhanced reference memory system for storing and retrieving trading decisions.
    
    This system enables AlphaAxiom to:
    1. Store complete decision contexts with outcomes
    2. Find similar historical situations
    3. Learn from past successes and failures
    4. Support counterfactual analysis
    """
    
    def __init__(self, d1_db, kv_store, vectorize_client=None):
        """
        Initialize the Reference Memory System.
        
        Args:
            d1_db: D1 database connection for persistent storage
            kv_store: KV store for fast access to memory data
            vectorize_client: Vectorize client for vector operations (optional)
        """
        self.d1 = d1_db
        self.kv = kv_store
        self.vectorize = vectorize_client
        self.memory_cache = {}
        self.embedding_dimension = 768  # Standard for many embedding models
        
        # Memory parameters
        self.memory_params = {
            'similarity_threshold': 0.75,
            'max_results': 10,
            'cache_ttl': 3600,  # 1 hour
            'embedding_model': 'text-embedding-ada-002'
        }
    
    async def record_decision(
        self, 
        symbol: str,
        action: str,
        confidence: float,
        context: Dict[str, Any],
        expected_outcome: float,
        actual_outcome: float = None
    ) -> str:
        """
        Record a trading decision with its context and outcome.
        
        Args:
            symbol: Trading symbol
            action: BUY, SELL, or HOLD
            confidence: Decision confidence (0.0 - 1.0)
            context: Full decision context
            expected_outcome: Expected result
            actual_outcome: Actual result (if available)
            
        Returns:
            String representing the decision ID
        """
        import uuid
        
        # Create decision ID
        decision_id = str(uuid.uuid4())[:12]
        
        # Create context object
        context_obj = TradingDecisionContext(
            symbol=symbol,
            price_data=context.get('price_data', {}),
            technical_indicators=context.get('technical_indicators', {}),
            market_sentiment=context.get('market_sentiment', {}),
            news_sentiment=context.get('news_sentiment', {}),
            social_sentiment=context.get('social_sentiment', {}),
            risk_metrics=context.get('risk_metrics', {}),
            timestamp=datetime.now(),
            additional_context=context.get('additional_context', {})
        )
        
        # Calculate outcome metrics if actual outcome is provided
        prediction_error = None
        was_correct = None
        if actual_outcome is not None:
            prediction_error = actual_outcome - expected_outcome
            was_correct = (
                (action == "BUY" and actual_outcome > 0) or
                (action == "SELL" and actual_outcome < 0) or
                (action == "HOLD" and abs(actual_outcome) < 0.01)
            )
        
        # Generate embedding from context
        embedding = await self._generate_decision_embedding(context_obj)
        
        # Create decision record
        record = TradingDecisionRecord(
            decision_id=decision_id,
            symbol=symbol,
            action=action,
            confidence=confidence,
            context=context_obj,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome or 0.0,
            prediction_error=prediction_error or 0.0,
            was_correct=was_correct,
            embedding=embedding,
            metadata={
                'source': 'alphaaxiom',
                'version': '2.0',
                'tags': ['trading_decision', 'reference_memory']
            }
        )
        
        # Store in database
        await self._store_decision_record(record)
        
        # Update cache
        self.memory_cache[decision_id] = record
        
        # Index in vector database if available
        if self.vectorize:
            await self._index_in_vector_db(record)
        
        return decision_id
    
    async def find_similar_decisions(
        self, 
        context: Dict[str, Any], 
        top_k: int = 5
    ) -> List[SimilarDecision]:
        """
        Find similar historical decisions based on current context.
        
        Args:
            context: Current decision context
            top_k: Number of similar decisions to return
            
        Returns:
            List of similar decisions
        """
        # Create context object
        context_obj = TradingDecisionContext(
            symbol=context.get('symbol', ''),
            price_data=context.get('price_data', {}),
            technical_indicators=context.get('technical_indicators', {}),
            market_sentiment=context.get('market_sentiment', {}),
            news_sentiment=context.get('news_sentiment', {}),
            social_sentiment=context.get('social_sentiment', {}),
            risk_metrics=context.get('risk_metrics', {}),
            timestamp=datetime.now(),
            additional_context=context.get('additional_context', {})
        )
        
        # Generate embedding for current context
        query_embedding = await self._generate_decision_embedding(context_obj)
        
        # Search for similar decisions
        if self.vectorize:
            return await self._search_vector_db(query_embedding, top_k)
        
        # Fallback to database search
        return await self._search_database(query_embedding, top_k)
    
    async def update_decision_outcome(
        self, 
        decision_id: str, 
        actual_outcome: float
    ) -> bool:
        """
        Update a decision record with its actual outcome.
        
        Args:
            decision_id: ID of the decision to update
            actual_outcome: Actual result of the decision
            
        Returns:
            Boolean indicating success
        """
        # Retrieve existing record
        record = await self._get_decision_record(decision_id)
        if not record:
            return False
        
        # Update outcome metrics
        record.actual_outcome = actual_outcome
        record.prediction_error = actual_outcome - record.expected_outcome
        record.was_correct = (
            (record.action == "BUY" and actual_outcome > 0) or
            (record.action == "SELL" and actual_outcome < 0) or
            (record.action == "HOLD" and abs(actual_outcome) < 0.01)
        )
        
        # Update timestamp
        record.timestamp = datetime.now()
        
        # Store updated record
        await self._store_decision_record(record)
        
        # Update cache
        self.memory_cache[decision_id] = record
        
        # Update vector database if available
        if self.vectorize:
            await self._update_vector_db_entry(record)
        
        return True
    
    async def _generate_decision_embedding(
        self, 
        context: TradingDecisionContext
    ) -> List[float]:
        """
        Generate embedding for a decision context.
        
        Args:
            context: Trading decision context
            
        Returns:
            List of floats representing the embedding
        """
        # Create a comprehensive text representation of the context
        context_text = self._context_to_text(context)
        
        # Check cache first
        cache_key = f"decision_embedding_{hash(context_text)}"
        cached = await self.kv.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # In a production implementation, this would call an actual 
        # embedding service. In practice, you might use OpenAI embeddings, 
        # Sentence Transformers, etc.
        
        # Simple mock embedding - in reality, this would be a proper vector
        np.random.seed(hash(context_text) % (2**32))  # For reproducible "embeddings"
        embedding = np.random.randn(self.embedding_dimension).tolist()
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        # Cache the embedding
        await self.kv.put(cache_key, json.dumps(embedding))
        
        return embedding
    
    def _context_to_text(self, context: TradingDecisionContext) -> str:
        """
        Convert decision context to text for embedding.
        
        Args:
            context: Trading decision context
            
        Returns:
            String representation of the context
        """
        # Create a comprehensive text representation
        parts = []
        
        # Symbol and basic info
        parts.append(f"Symbol: {context.symbol}")
        
        # Price data
        if context.price_data:
            parts.append(f"Price: {context.price_data}")
        
        # Technical indicators
        if context.technical_indicators:
            parts.append(f"Technical Indicators: {context.technical_indicators}")
        
        # Sentiment data
        if context.market_sentiment:
            parts.append(f"Market Sentiment: {context.market_sentiment}")
        if context.news_sentiment:
            parts.append(f"News Sentiment: {context.news_sentiment}")
        if context.social_sentiment:
            parts.append(f"Social Sentiment: {context.social_sentiment}")
        
        # Risk metrics
        if context.risk_metrics:
            parts.append(f"Risk Metrics: {context.risk_metrics}")
        
        # Additional context
        if context.additional_context:
            parts.append(f"Additional Context: {context.additional_context}")
        
        return " | ".join(parts)
    
    async def _store_decision_record(self, record: TradingDecisionRecord) -> None:
        """
        Store a decision record in the database.
        
        Args:
            record: TradingDecisionRecord to store
        """
        query = """
            INSERT OR REPLACE INTO reference_memory 
            (decision_id, symbol, action, confidence, context, 
             expected_outcome, actual_outcome, prediction_error, was_correct,
             embedding, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.d1.execute(
            query,
            record.decision_id,
            record.symbol,
            record.action,
            record.confidence,
            json.dumps({
                'price_data': record.context.price_data,
                'technical_indicators': record.context.technical_indicators,
                'market_sentiment': record.context.market_sentiment,
                'news_sentiment': record.context.news_sentiment,
                'social_sentiment': record.context.social_sentiment,
                'risk_metrics': record.context.risk_metrics,
                'additional_context': record.context.additional_context,
                'timestamp': record.context.timestamp.isoformat()
            }),
            record.expected_outcome,
            record.actual_outcome,
            record.prediction_error,
            1 if record.was_correct else 0,
            json.dumps(record.embedding),
            record.timestamp.isoformat(),
            json.dumps(record.metadata)
        )
    
    async def _get_decision_record(
        self, 
        decision_id: str
    ) -> Optional[TradingDecisionRecord]:
        """
        Retrieve a decision record by ID.
        
        Args:
            decision_id: ID of the record to retrieve
            
        Returns:
            TradingDecisionRecord object or None
        """
        # Check cache first
        if decision_id in self.memory_cache:
            record = self.memory_cache[decision_id]
            # Check if still fresh
            cache_ttl = self.memory_params['cache_ttl']
            if (datetime.now() - record.timestamp).seconds < cache_ttl:
                return record
        
        # Check database
        result = await self.d1.execute(
            "SELECT * FROM reference_memory WHERE decision_id = ?",
            decision_id
        )
        
        if not result:
            return None
        
        row = result[0]
        context_data = json.loads(row['context'])
        
        context = TradingDecisionContext(
            symbol=row['symbol'],
            price_data=context_data.get('price_data', {}),
            technical_indicators=context_data.get('technical_indicators', {}),
            market_sentiment=context_data.get('market_sentiment', {}),
            news_sentiment=context_data.get('news_sentiment', {}),
            social_sentiment=context_data.get('social_sentiment', {}),
            risk_metrics=context_data.get('risk_metrics', {}),
            timestamp=datetime.fromisoformat(context_data.get('timestamp')),
            additional_context=context_data.get('additional_context', {})
        )
        
        record = TradingDecisionRecord(
            decision_id=row['decision_id'],
            symbol=row['symbol'],
            action=row['action'],
            confidence=row['confidence'],
            context=context,
            expected_outcome=row['expected_outcome'],
            actual_outcome=row['actual_outcome'],
            prediction_error=row['prediction_error'],
            was_correct=bool(row['was_correct']),
            embedding=json.loads(row['embedding']),
            timestamp=datetime.fromisoformat(row['timestamp']),
            metadata=json.loads(row['metadata'])
        )
        
        # Cache the record
        self.memory_cache[decision_id] = record
        
        return record
    
    async def _search_database(
        self, 
        query_embedding: List[float], 
        top_k: int
    ) -> List[SimilarDecision]:
        """
        Search for decision records in the database using cosine similarity.
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return
            
        Returns:
            List of SimilarDecision objects
        """
        # Retrieve recent entries (in practice, you'd use a more efficient method)
        results = await self.d1.execute(
            "SELECT * FROM reference_memory ORDER BY timestamp DESC LIMIT 100"
        )
        
        if not results:
            return []
        
        # Calculate similarities
        similarities = []
        for row in results:
            entry_embedding = json.loads(row['embedding'])
            similarity = self._cosine_similarity(query_embedding, entry_embedding)
            
            threshold = self.memory_params['similarity_threshold']
            if similarity >= threshold:
                context_data = json.loads(row['context'])
                context_summary = {
                    'price_data': context_data.get('price_data', {}),
                    'technical_indicators': context_data.get('technical_indicators', {}),
                    'market_sentiment': context_data.get('market_sentiment', {}),
                    'risk_metrics': context_data.get('risk_metrics', {})
                }
                
                similar_decision = SimilarDecision(
                    decision_id=row['decision_id'],
                    symbol=row['symbol'],
                    action=row['action'],
                    confidence=row['confidence'],
                    similarity=similarity,
                    expected_outcome=row['expected_outcome'],
                    actual_outcome=row['actual_outcome'],
                    was_correct=bool(row['was_correct']),
                    context_summary=context_summary,
                    timestamp=datetime.fromisoformat(row['timestamp'])
                )
                similarities.append((similarity, similar_decision))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [result for _, result in similarities[:top_k]]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Float representing cosine similarity
        """
        # Convert to numpy arrays
        a_arr = np.array(a)
        b_arr = np.array(b)
        
        # Calculate dot product
        dot_product = np.dot(a_arr, b_arr)
        
        # Calculate magnitudes
        magnitude_a = np.linalg.norm(a_arr)
        magnitude_b = np.linalg.norm(b_arr)
        
        # Calculate cosine similarity
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return float(dot_product / (magnitude_a * magnitude_b))
    
    async def _index_in_vector_db(self, record: TradingDecisionRecord) -> None:
        """
        Index a decision record in the vector database.
        
        Args:
            record: TradingDecisionRecord to index
        """
        # This would interface with Cloudflare Vectorize or similar service
        # Implementation depends on the specific vector database being used
        pass
    
    async def _search_vector_db(
        self, 
        query_embedding: List[float], 
        top_k: int
    ) -> List[SimilarDecision]:
        """
        Search for decision records in the vector database.
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return
            
        Returns:
            List of SimilarDecision objects
        """
        # This would interface with Cloudflare Vectorize or similar service
        # Implementation depends on the specific vector database being used
        
        # Fallback to database search
        return await self._search_database(query_embedding, top_k)
    
    async def _update_vector_db_entry(self, record: TradingDecisionRecord) -> None:
        """
        Update a decision record in the vector database.
        
        Args:
            record: TradingDecisionRecord to update
        """
        # This would interface with Cloudflare Vectorize or similar service
        pass
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the reference memory.
        
        Returns:
            Dictionary with memory statistics
        """
        result = await self.d1.execute(
            "SELECT COUNT(*) as total_records, "
            "MAX(timestamp) as last_updated, "
            "AVG(confidence) as avg_confidence, "
            "AVG(CASE WHEN was_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy_rate "
            "FROM reference_memory"
        )
        
        if result:
            row = result[0]
            return {
                'total_records': row['total_records'],
                'last_updated': row['last_updated'],
                'average_confidence': row['avg_confidence'],
                'accuracy_rate': row['accuracy_rate'],
                'cache_size': len(self.memory_cache),
                'dimension': self.embedding_dimension
            }
        
        return {
            'total_records': 0,
            'last_updated': None,
            'average_confidence': 0.0,
            'accuracy_rate': 0.0,
            'cache_size': len(self.memory_cache),
            'dimension': self.embedding_dimension
        }