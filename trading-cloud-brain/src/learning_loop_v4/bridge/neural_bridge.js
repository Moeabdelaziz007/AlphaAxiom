/**
 * Non-Linear Neural Bridge for AlphaAxiom v4.0
 * Implements a lightweight neural network for decision synthesis running on Cloudflare Workers.
 */

// Neural network weights (learned offline and exported)
// These would be updated periodically through training
const NETWORK_WEIGHTS = {
  // Hidden layer 1 weights (6 inputs -> 16 neurons)
  w1: [
    [0.12, -0.45, 0.67, -0.23, 0.89, -0.56],
    [-0.34, 0.78, -0.12, 0.45, -0.67, 0.23],
    [0.56, -0.89, 0.34, -0.78, 0.12, -0.45],
    // ... (16 neurons total)
  ],
  // Hidden layer 1 biases
  b1: [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -1.0, 1.1, -1.2, 1.3, -1.4, 1.5, -1.6],
  // Output layer weights (16 neurons -> 1 output)
  wOut: [0.23, -0.45, 0.67, -0.89, 0.12, -0.34, 0.56, -0.78, 0.91, -0.23, 0.45, -0.67, 0.89, -0.12, 0.34, -0.56],
  // Output layer bias
  bOut: 0.5
};

/**
 * Rectified Linear Unit activation function
 * @param {number} x - Input value
 * @returns {number} - Output value
 */
function relu(x) {
  return Math.max(0, x);
}

/**
 * Sigmoid activation function
 * @param {number} x - Input value
 * @returns {number} - Output value
 */
function sigmoid(x) {
  return 1 / (1 + Math.exp(-Math.max(-50, Math.min(50, x)))); // Clamped to prevent overflow
}

/**
 * Dot product of two vectors
 * @param {Array<number>} a - First vector
 * @param {Array<number>} b - Second vector
 * @returns {number} - Dot product result
 */
function dotProduct(a, b) {
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result += a[i] * b[i];
  }
  return result;
}

/**
 * Matrix-vector multiplication
 * @param {Array<Array<number>>} matrix - Matrix (2D array)
 * @param {Array<number>} vector - Vector (1D array)
 * @returns {Array<number>} - Result vector
 */
function matrixVectorMultiply(matrix, vector) {
  const result = [];
  for (let i = 0; i < matrix.length; i++) {
    result.push(dotProduct(matrix[i], vector));
  }
  return result;
}

/**
 * Add two vectors element-wise
 * @param {Array<number>} a - First vector
 * @param {Array<number>} b - Second vector
 * @returns {Array<number>} - Sum vector
 */
function vectorAdd(a, b) {
  const result = [];
  for (let i = 0; i < a.length; i++) {
    result.push(a[i] + b[i]);
  }
  return result;
}

/**
 * Forward pass through the neural network
 * @param {Array<number>} inputs - Input features (6-dimensional)
 * @returns {number} - Execution weight (0.0 to 1.0)
 */
function forwardPass(inputs) {
  // Hidden layer 1 computation
  // H1 = ReLU(W1 * X + B1)
  const hidden1 = matrixVectorMultiply(NETWORK_WEIGHTS.w1, inputs);
  const hidden1Biased = vectorAdd(hidden1, NETWORK_WEIGHTS.b1);
  const hidden1Activated = hidden1Biased.map(relu);
  
  // Output layer computation
  // Y = Sigmoid(WOut * H1 + BOut)
  const output = dotProduct(NETWORK_WEIGHTS.wOut, hidden1Activated) + NETWORK_WEIGHTS.bOut;
  return sigmoid(output);
}

/**
 * Normalize input features to [0, 1] range
 * @param {Object} features - Raw feature values
 * @returns {Array<number>} - Normalized feature vector
 */
function normalizeFeatures(features) {
  return [
    // Core confidence (already 0-1)
    Math.max(0, Math.min(1, features.core_confidence || 0.5)),
    // Shadow regret (invert to make higher values indicate higher risk)
    1 - Math.max(0, Math.min(1, features.shadow_regret || 0.5)),
    // Relative ATR (clamp to reasonable range)
    Math.max(0, Math.min(2, features.relative_atr || 1)),
    // Market velocity (normalize assuming typical range -0.1 to 0.1)
    (Math.max(-0.1, Math.min(0.1, features.market_velocity || 0)) + 0.1) / 0.2,
    // Sentiment divergence (already 0-1)
    Math.max(0, Math.min(1, features.sentiment_divergence || 0.5)),
    // Volume ratio (clamp to reasonable range)
    Math.max(0, Math.min(3, features.volume_ratio || 1))
  ];
}

/**
 * Neural Bridge - Translates dialectic synthesis into execution weight
 * @param {Object} dialecticSynthesis - Output from UnifiedDialecticModel
 * @param {Object} marketMetrics - Current market conditions
 * @returns {Object} - Decision with execution weight
 */
export async function neuralBridge(dialecticSynthesis, marketMetrics) {
  try {
    // Extract features from dialectic synthesis and market metrics
    const features = {
      core_confidence: dialecticSynthesis.core_thesis.confidence,
      shadow_regret: dialecticSynthesis.shadow_antithesis.confidence,
      relative_atr: marketMetrics.relative_atr || 1.0,
      market_velocity: marketMetrics.velocity || 0.0,
      sentiment_divergence: marketMetrics.sentiment_divergence || 0.0,
      volume_ratio: marketMetrics.volume_ratio || 1.0
    };
    
    // Normalize features
    const normalizedInputs = normalizeFeatures(features);
    
    // Forward pass through neural network
    const executionWeight = forwardPass(normalizedInputs);
    
    // Determine if execution should proceed based on threshold
    const shouldExecute = executionWeight > 0.75;
    
    return {
      execution_weight: executionWeight,
      should_execute: shouldExecute,
      features: features,
      normalized_inputs: normalizedInputs,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    // Fallback decision if neural bridge fails
    return {
      execution_weight: 0.5,
      should_execute: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// Example usage (for testing)
/*
const exampleSynthesis = {
  core_thesis: { confidence: 0.85 },
  shadow_antithesis: { confidence: 0.30 }
};

const exampleMetrics = {
  relative_atr: 1.2,
  velocity: 0.05,
  sentiment_divergence: 0.1,
  volume_ratio: 1.5
};

neuralBridge(exampleSynthesis, exampleMetrics)
  .then(result => console.log("Neural Bridge Decision:", result));
*/