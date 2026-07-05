/*import { GEMINI_API_KEY } from "../config";

function buildPrompt(city, conditions) {
  return `
You are GeoHealth AI, a NON-DIAGNOSTIC health risk assessment system.

STRICT SYSTEM BEHAVIOR:

- You MUST return ONLY valid JSON
- If anything is invalid → return:
  { "error": "reason" }

CRITICAL CONSTRAINTS:

1. DO NOT diagnose diseases
2. DO NOT predict medical outcomes
3. ONLY output risk levels: low, moderate, high
4. MUST be population-level reasoning
5. MUST NOT hallucinate real-time data
6. Confidence must be between 0.5 and 0.9
7. If input is unclear → assume safe defaults
8. If city is not valid → return error
9. No extra text outside JSON

RISK LOGIC:

- Smoking → increases respiratory risk
- Sedentary lifestyle → increases cardiovascular risk
- Multiple conditions → increase overall risk
- Healthy lifestyle → reduce risk

OUTPUT FORMAT (STRICT):

{
  "risk_level": "low|moderate|high",
  "confidence": number,
  "reasoning": ["string"],
  "recommendations": ["string"]
}

USER INPUT:
City: ${city}
Conditions: ${conditions}
`;
}*/

import { GEMINI_API_KEY } from "../config";

function buildPrompt(city, text) {
  return `
You are GeoHealth AI backend simulator.

Return ONLY JSON.

VALIDATION:
- Age must be between 0 and 120
- If invalid → valid=false

EXTRACTION:
- Extract age
- Extract conditions (diabetes, hypertension, etc.)
- Detect smoking → smoker=true
- If "healthy" → no conditions

RISK RULES:
- Age > 60 → higher risk
- Smoking → respiratory risk
- Diabetes → metabolic risk

ENVIRONMENT:
- Delhi → high pollution (~0.85)
- Others → moderate (~0.5)

OUTPUT:

{
  "valid": true,
  "errors": [],
  "nlp_features": {
  "age": number,
  "conditions": [],
  "family_history": [],
  "lifestyle": {
    "smoker": boolean,
    "activity_level": "low|medium|high"
  },
  "pollution": {
    "environment": "urban|rural",
    "severity": "low|moderate|high"
  },
  "raw_entities": []
}
  },
  "ml_features": {
    "pollution_score": number,
    "climate_score": number,
    "environmental_risk": number
  },
  "prediction": {
    "risk_score": number,
    "risk_level": "Low|Moderate|High",
    "primary_condition": "string",
    "disease_groups": []
  },
  "recommendations": []
}

USER INPUT:
City: ${city}
Text: ${text}
`;
}

export async function callGemini(city, conditions) {
  const prompt = buildPrompt(city, conditions);

  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            role: "user",
            parts: [{ text: prompt }],
          },
        ],
        generationConfig: {
          temperature: 0.3,
        },
      }),
    }
  );

  const data = await res.json();
  console.log("FULL RESPONSE:", data);

  if (data.error) {
    throw new Error(data.error.message);
  }

  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

  if (!text) {
    throw new Error("Empty response");
  }

  const match = text.match(/\{[\s\S]*\}/);

  const parsed = JSON.parse(match[0]);

// Basic fallback protection
if (!parsed.nlp_features) {
  throw new Error("Invalid structured response from Gemini");
}

// ✅ Normalize missing fields (VERY IMPORTANT)
parsed.nlp_features = {
  age: parsed.nlp_features?.age ?? null,
  conditions: parsed.nlp_features?.conditions ?? [],
  family_history: parsed.nlp_features?.family_history ?? [],
  lifestyle: parsed.nlp_features?.lifestyle ?? {
    smoker: false,
    activity_level: "low",
  },
  pollution: parsed.nlp_features?.pollution ?? {
    environment: "urban",
    severity: "moderate",
  },
  raw_entities: parsed.nlp_features?.raw_entities ?? [],
};

parsed.ml_features = {
  pollution_score: parsed.ml_features?.pollution_score ?? 0.5,
  climate_score: parsed.ml_features?.climate_score ?? 0.4,
  environmental_risk:
    parsed.ml_features?.environmental_risk ??
    (parsed.ml_features?.pollution_score + parsed.ml_features?.climate_score) / 2,
};

return parsed;
}