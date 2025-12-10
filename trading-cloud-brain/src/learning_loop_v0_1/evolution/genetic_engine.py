"""
Differential Evolution Engine for AlphaAxiom v1.0
Implements continuous strategy mutation and self-improvement mechanisms.
"""

import json
import random
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StrategyGenotype:
    """Represents a strategy as a vector of hyperparameters"""
    prompt_temperature: float  # 0.1 to 1.0
    shadow_risk_penalty: float  # Scalar weight for shadow regret
    bridge_weights: List[List[float]]  # Neural bridge MLP weights
    lookback_period: int  # Hours of context (24 or 48)
    fitness_score: float = 0.0
    generation: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DifferentialEvolutionEngine:
    """
    Genetic engine for continuous self-improvement of the AlphaAxiom system.
    Uses Differential Evolution to optimize trading strategies in a rugged landscape.
    """
    
    def __init__(self, population_size: int = 50, mutation_factor: float = 0.8, 
                 crossover_rate: float = 0.7):
        """
        Initialize the Differential Evolution Engine.
        
        Args:
            population_size: Number of candidate strategies in population
            mutation_factor: Scaling factor for differential mutation (F)
            crossover_rate: Crossover probability (CR)
        """
        self.population_size = population_size
        self.mutation_factor = mutation_factor
        self.crossover_rate = crossover_rate
        self.population: List[StrategyGenotype] = []
        self.generation = 0
        self.best_strategy = None
        self.fitness_history = []
    
    def initialize_population(self) -> List[StrategyGenotype]:
        """
        Create initial population of strategy variants.
        
        Returns:
            List of randomly initialized strategy genotypes
        """
        population = []
        
        for i in range(self.population_size):
            # Randomly initialize hyperparameters within valid ranges
            genotype = StrategyGenotype(
                prompt_temperature=random.uniform(0.1, 1.0),
                shadow_risk_penalty=random.uniform(0.1, 2.0),
                bridge_weights=self._random_bridge_weights(),
                lookback_period=random.choice([24, 48]),
                generation=0,
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "variant_id": f"VAR_{i:03d}"
                }
            )
            population.append(genotype)
        
        self.population = population
        return population
    
    def _random_bridge_weights(self) -> List[List[float]]:
        """
        Generate random weights for the neural bridge MLP.
        
        Returns:
            Random weight matrix for the neural bridge
        """
        # Simplified representation - in practice this would match neural_bridge.js structure
        hidden_layer_weights = [[random.uniform(-1, 1) for _ in range(6)] for _ in range(16)]
        output_weights = [random.uniform(-1, 1) for _ in range(16)]
        return [hidden_layer_weights, output_weights]
    
    def evaluate_fitness(self, genotype: StrategyGenotype, 
                       crime_scenes: List[Dict[str, Any]]) -> float:
        """
        Evaluate the fitness of a strategy against historical crime scenes.
        
        Args:
            genotype: Strategy to evaluate
            crime_scenes: Historical market snapshots for backtesting
            
        Returns:
            Fitness score (higher is better)
        """
        # In a real implementation, this would:
        # 1. Run each crime scene through the strategy with these parameters
        # 2. Calculate performance metrics (Sharpe Ratio, Max Drawdown, etc.)
        # 3. Apply the fitness function: Fitness = SharpeRatio × (1 - MaxDrawdown)
        
        # For simulation, we'll calculate a synthetic fitness score
        # based on how well the parameters align with "optimal" values
        temperature_fitness = 1.0 - abs(genotype.prompt_temperature - 0.7) / 0.6
        risk_penalty_fitness = 1.0 - abs(genotype.shadow_risk_penalty - 1.0) / 1.0
        lookback_fitness = 1.0 if genotype.lookback_period == 48 else 0.8
        
        # Combine factors with weighted importance
        fitness = (
            0.4 * temperature_fitness + 
            0.3 * risk_penalty_fitness + 
            0.3 * lookback_fitness
        )
        
        # Add some noise to simulate real-world variability
        fitness += random.uniform(-0.1, 0.1)
        fitness = max(0.0, min(1.0, fitness))  # Clamp to [0,1]
        
        return fitness
    
    def mutate(self, target_idx: int) -> StrategyGenotype:
        """
        Create a mutant candidate using Differential Evolution.
        
        DE/best/1/bin strategy:
        V_{i,G+1} = X_{best,G} + F · (X_{r1,G} - X_{r2,G})
        
        Args:
            target_idx: Index of target individual
            
        Returns:
            Mutant strategy genotype
        """
        # Select three distinct individuals different from target
        candidates = list(range(len(self.population)))
        candidates.remove(target_idx)
        r1, r2, r3 = random.sample(candidates, 3)
        
        # Get the best individual
        best_idx = self._get_best_individual_index()
        
        # Get individuals
        x_best = self.population[best_idx]
        x_r1 = self.population[r1]
        x_r2 = self.population[r2]
        
        # Create mutant variant
        mutant = StrategyGenotype(
            prompt_temperature=x_best.prompt_temperature + self.mutation_factor * 
                             (x_r1.prompt_temperature - x_r2.prompt_temperature),
            shadow_risk_penalty=x_best.shadow_risk_penalty + self.mutation_factor * 
                               (x_r1.shadow_risk_penalty - x_r2.shadow_risk_penalty),
            bridge_weights=self._mutate_bridge_weights(
                x_best.bridge_weights, x_r1.bridge_weights, x_r2.bridge_weights
            ),
            lookback_period=x_best.lookback_period,
            generation=self.generation + 1,
            metadata={
                "created_at": datetime.now().isoformat(),
                "variant_id": f"MUT_{self.generation:03d}_{target_idx:02d}",
                "parents": [
                    x_best.metadata.get("variant_id", "UNKNOWN"),
                    x_r1.metadata.get("variant_id", "UNKNOWN"),
                    x_r2.metadata.get("variant_id", "UNKNOWN")
                ]
            }
        )
        
        # Ensure parameters stay within valid ranges
        mutant.prompt_temperature = max(0.1, min(1.0, mutant.prompt_temperature))
        mutant.shadow_risk_penalty = max(0.1, min(2.0, mutant.shadow_risk_penalty))
        
        return mutant
    
    def _mutate_bridge_weights(self, best_weights: List, r1_weights: List, 
                              r2_weights: List) -> List:
        """
        Mutate neural bridge weights using differential evolution.
        
        Args:
            best_weights: Best individual's weights
            r1_weights: First random individual's weights
            r2_weights: Second random individual's weights
            
        Returns:
            Mutated weight matrix
        """
        # Simplified mutation - in practice would handle the full weight structure
        mutated_weights = []
        
        for layer_idx, (best_layer, r1_layer, r2_layer) in enumerate(
            zip(best_weights, r1_weights, r2_weights)
        ):
            if isinstance(best_layer[0], list):  # Hidden layer
                mutated_layer = []
                for neuron_idx, (best_neuron, r1_neuron, r2_neuron) in enumerate(
                    zip(best_layer, r1_layer, r2_layer)
                ):
                    mutated_neuron = [
                        best_w + self.mutation_factor * (r1_w - r2_w)
                        for best_w, r1_w, r2_w in zip(best_neuron, r1_neuron, r2_neuron)
                    ]
                    mutated_layer.append(mutated_neuron)
                mutated_weights.append(mutated_layer)
            else:  # Output layer
                mutated_layer = [
                    best_w + self.mutation_factor * (r1_w - r2_w)
                    for best_w, r1_w, r2_w in zip(best_layer, r1_layer, r2_layer)
                ]
                mutated_weights.append(mutated_layer)
        
        return mutated_weights
    
    def crossover(self, target: StrategyGenotype, 
                  mutant: StrategyGenotype) -> StrategyGenotype:
        """
        Perform crossover between target and mutant individuals.
        
        Args:
            target: Original individual
            mutant: Mutant individual
            
        Returns:
            Trial individual after crossover
        """
        # Binomial crossover - each parameter is inherited from mutant with probability CR
        trial = StrategyGenotype(
            prompt_temperature=(
                mutant.prompt_temperature 
                if random.random() < self.crossover_rate 
                else target.prompt_temperature
            ),
            shadow_risk_penalty=(
                mutant.shadow_risk_penalty 
                if random.random() < self.crossover_rate 
                else target.shadow_risk_penalty
            ),
            bridge_weights=(
                mutant.bridge_weights 
                if random.random() < self.crossover_rate 
                else target.bridge_weights
            ),
            lookback_period=(
                mutant.lookback_period 
                if random.random() < self.crossover_rate 
                else target.lookback_period
            ),
            generation=mutant.generation,
            metadata={
                "created_at": datetime.now().isoformat(),
                "variant_id": f"TRIAL_{self.generation:03d}",
                "parent": target.metadata.get("variant_id", "UNKNOWN"),
                "mutant": mutant.metadata.get("variant_id", "UNKNOWN")
            }
        )
        
        return trial
    
    def select(self, target_idx: int, trial: StrategyGenotype, 
               crime_scenes: List[Dict[str, Any]]) -> bool:
        """
        Select between target and trial individuals based on fitness.
        
        Args:
            target_idx: Index of target individual
            trial: Trial individual
            crime_scenes: Historical data for evaluation
            
        Returns:
            True if trial is selected, False if target is retained
        """
        # Evaluate fitness of trial individual
        trial_fitness = self.evaluate_fitness(trial, crime_scenes)
        trial.fitness_score = trial_fitness
        
        # Get fitness of target individual
        target_fitness = self.population[target_idx].fitness_score
        
        # Select the better individual
        return trial_fitness > target_fitness
    
    def evolve_generation(self, crime_scenes: List[Dict[str, Any]]):
        """
        Evolve the population for one generation.
        
        Args:
            crime_scenes: Historical market snapshots for evaluation
        """
        # Evaluate initial population if not already done
        if self.generation == 0:
            for individual in self.population:
                individual.fitness_score = self.evaluate_fitness(individual, crime_scenes)
        
        # Evolve each individual
        for i in range(len(self.population)):
            # Create mutant
            mutant = self.mutate(i)
            
            # Create trial individual through crossover
            trial = self.crossover(self.population[i], mutant)
            
            # Evaluate trial fitness
            trial_fitness = self.evaluate_fitness(trial, crime_scenes)
            trial.fitness_score = trial_fitness
            
            # Selection - replace target if trial is better
            if trial_fitness > self.population[i].fitness_score:
                self.population[i] = trial
        
        # Update generation counter
        self.generation += 1
        
        # Track best strategy
        best_idx = self._get_best_individual_index()
        self.best_strategy = self.population[best_idx]
        
        # Track fitness history
        avg_fitness = sum(ind.fitness_score for ind in self.population) / len(self.population)
        self.fitness_history.append({
            "generation": self.generation,
            "best_fitness": self.best_strategy.fitness_score,
            "avg_fitness": avg_fitness,
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_best_individual_index(self) -> int:
        """
        Get the index of the best individual in the population.
        
        Returns:
            Index of the individual with highest fitness
        """
        best_idx = 0
        best_fitness = self.population[0].fitness_score
        
        for i, individual in enumerate(self.population):
            if individual.fitness_score > best_fitness:
                best_idx = i
                best_fitness = individual.fitness_score
                
        return best_idx
    
    def get_shadow_deployment_candidate(self, 
                                     performance_threshold: float = 0.05) -> StrategyGenotype:
        """
        Get a candidate strategy for shadow deployment if it significantly 
        outperforms the current best.
        
        Args:
            performance_threshold: Minimum improvement required (5% default)
            
        Returns:
            Strategy candidate for shadow deployment or None
        """
        if not self.best_strategy:
            return None
            
        # In a real implementation, this would compare against the currently
        # deployed production strategy
        # For now, we'll just check if the best strategy meets a minimum threshold
        if self.best_strategy.fitness_score > performance_threshold:
            return self.best_strategy
            
        return None


# Example usage
if __name__ == "__main__":
    # Initialize the engine
    engine = DifferentialEvolutionEngine(population_size=20)
    
    # Create initial population
    population = engine.initialize_population()
    print(f"Initialized population with {len(population)} individuals")
    
    # Simulate crime scenes (historical data)
    crime_scenes = [{"id": i, "data": f"crime_scene_{i}"} for i in range(100)]
    
    # Evolve for a few generations
    for gen in range(5):
        engine.evolve_generation(crime_scenes)
        best_idx = engine._get_best_individual_index()
        best_fitness = engine.population[best_idx].fitness_score
        avg_fitness = sum(ind.fitness_score for ind in engine.population) / len(engine.population)
        print(f"Generation {gen+1}: Best={best_fitness:.4f}, Avg={avg_fitness:.4f}")
    
    # Check for shadow deployment candidate
    candidate = engine.get_shadow_deployment_candidate()
    if candidate:
        print(f"Shadow deployment candidate found with fitness: {candidate.fitness_score:.4f}")
    else:
        print("No suitable candidate for shadow deployment")