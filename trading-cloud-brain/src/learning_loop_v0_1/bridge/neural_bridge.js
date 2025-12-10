// Neural Bridge for AlphaAxiom v0.1 Beta
// Pure JavaScript implementation for Cloudflare Workers Edge Compute
// Sub-10ms latency, no heavy ML libraries

/**
 * Neural Bridge Configuration
 * Weights evolved via Differential Evolution
 */
const BRIDGE_CONFIG = {
  // Input features: [core_conf, shadow_regret, atr_ratio, sentiment, velocity, bias]
  INPUT_SIZE: 6,
  HIDDEN_SIZE: 16,
  OUTPUT_SIZE: 1,

  // Evolved weights (from Differential Evolution)
  // Layer 1: INPUT -> HIDDEN (6 x 16 matrix)
  WEIGHTS_L1: [
    [0.52, -0.81, 0.23, 0.15, -0.33, 0.12],
    [0.31, 0.47, -0.55, 0.08, 0.21, -0.18],
    [-0.22, 0.68, 0.41, -0.29, 0.11, 0.05],
    [0.45, -0.38, 0.19, 0.62, -0.15, 0.22],
    [0.18, 0.55, -0.42, 0.31, 0.48, -0.11],
    [-0.35, 0.29, 0.61, -0.18, 0.25, 0.33],
    [0.61, -0.45, 0.12, 0.38, -0.52, 0.08],
    [0.28, 0.72, -0.31, 0.15, 0.19, -0.25],
    [-0.15, 0.38, 0.55, -0.42, 0.31, 0.18],
    [0.42, -0.28, 0.35, 0.51, -0.18, 0.12],
    [0.19, 0.58, -0.22, 0.28, 0.45, -0.31],
    [-0.38, 0.45, 0.32, -0.55, 0.22, 0.15],
    [0.55, -0.32, 0.18, 0.42, -0.28, 0.21],
    [0.22, 0.65, -0.45, 0.18, 0.32, -0.15],
    [-0.28, 0.35, 0.48, -0.31, 0.25, 0.28],
    [0.48, -0.52, 0.25, 0.35, -0.42, 0.18]
  ],

  // Layer 2: HIDDEN -> OUTPUT (16 x 1)
  WEIGHTS_L2: [0.35, 0.28, -0.15, 0.42, 0.31, -0.22, 0.38, 0.25, -0.18, 0.45, 0.32, -0.28, 0.35, 0.22, -0.15, 0.38],

  // Biases
  BIAS_L1: [0.1, 0.05, -0.08, 0.12, 0.03, -0.05, 0.08, 0.02, -0.03, 0.1, 0.05, -0.08, 0.07, 0.03, -0.05, 0.06],
  BIAS_L2: 0.15
};

/**
 * Activation Functions
 */
const relu = (x) => Math.max(0, x);
const sigmoid = (x) => 1 / (1 + Math.exp(-x));

/**
 * Matrix operations (Pure JS, no libraries)
 */
function dotProduct(vec1, vec2) {
  return vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
}

/**
 * Forward pass through the Neural Bridge
 * @param {number[]} inputs - [core_conf, shadow_regret, atr_ratio, sentiment, velocity, 1.0]
 * @returns {number} - Execution weight (0.0 to 1.0)
 */
function forwardPass(inputs) {
  // Ensure bias is included
  if (inputs.length === 5) {
    inputs.push(1.0); // Bias input
  }

  // Layer 1: INPUT -> HIDDEN with ReLU
  const hidden = BRIDGE_CONFIG.WEIGHTS_L1.map((weights, i) => {
    const sum = dotProduct(weights, inputs) + BRIDGE_CONFIG.BIAS_L1[i];
    return relu(sum);
  });

  // Layer 2: HIDDEN -> OUTPUT with Sigmoid
  const output = dotProduct(hidden, BRIDGE_CONFIG.WEIGHTS_L2) + BRIDGE_CONFIG.BIAS_L2;
  return sigmoid(output);
}

/**
 * Calculate non-linear volatility adjustment (γ)
 * γ = 1 + max(0, ATR_norm - 1)²
 */
function calculateGamma(atrNorm) {
  const excess = Math.max(0, atrNorm - 1);
  return 1 + Math.pow(excess, 2);
}

/**
 * Calculate dynamic fear factor (β)
 * Updated based on Shadow accuracy
 */
function calculateBeta(recentResults) {
  // Default β
  let beta = 1.0;

  if (recentResults && recentResults.length > 0) {
    for (const result of recentResults) {
      if (result.shadowCorrect) {
        beta += 0.05; // Shadow was right to warn
      } else {
        beta -= 0.02; // Shadow was too cautious
      }
    }
  }

  // Clamp β between 0.5 and 2.0
  return Math.max(0.5, Math.min(2.0, beta));
}

/**
 * Main Bridge Decision Function
 */
function computeBridgeDecision(coreConf, shadowRegret, marketMetrics) {
  const { atrNorm, sentiment, velocity, recentResults } = marketMetrics;

  // Calculate adjustments
  const gamma = calculateGamma(atrNorm);
  const beta = calculateBeta(recentResults);

  // Prepare input vector
  const inputs = [
    coreConf,
    shadowRegret * beta * gamma, // Adjusted shadow regret
    atrNorm,
    sentiment || 0.5,
    velocity || 0,
    1.0 // Bias
  ];

  // Neural network forward pass
  const executionWeight = forwardPass(inputs);

  return {
    executionWeight,
    decision: interpretDecision(executionWeight),
    adjustments: {
      gamma: gamma.toFixed(3),
      beta: beta.toFixed(3),
      adjustedShadow: (shadowRegret * beta * gamma).toFixed(3)
    }
  };
}

/**
 * Interpret execution weight into trading decision
 */
function interpretDecision(weight) {
  if (weight >= 0.75) return "EXECUTE_FULL";
  if (weight >= 0.50) return "EXECUTE_REDUCED";
  if (weight >= 0.25) return "HOLD_WAIT";
  return "BLOCK_TRADE";
}

/**
 * Cloudflare Worker Handler
 */
export default {
  async fetch(request, env, ctx) {
    // CORS headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json"
    };

    // Handle preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const body = await request.json();

      const {
        core_confidence,
        shadow_regret,
        atr_norm = 1.0,
        sentiment = 0.5,
        velocity = 0,
        recent_results = []
      } = body;

      // Validate required inputs
      if (typeof core_confidence !== 'number' || typeof shadow_regret !== 'number') {
        return new Response(
          JSON.stringify({ error: "Missing required fields: core_confidence, shadow_regret" }),
          { status: 400, headers: corsHeaders }
        );
      }

      // Compute bridge decision
      const result = computeBridgeDecision(
        core_confidence,
        shadow_regret,
        {
          atrNorm: atr_norm,
          sentiment,
          velocity,
          recentResults: recent_results
        }
      );

      return new Response(
        JSON.stringify({
          ...result,
          timestamp: new Date().toISOString(),
          version: "v0.1-beta"
        }),
        { headers: corsHeaders }
      );

    } catch (error) {
      return new Response(
        JSON.stringify({ error: error.message }),
        { status: 500, headers: corsHeaders }
      );
    }
  }
};

// Export for testing
export { forwardPass, computeBridgeDecision, calculateGamma, calculateBeta };