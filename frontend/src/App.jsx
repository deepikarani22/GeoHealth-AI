import React, { useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Topbar from "./components/Topbar.jsx";
import { SummaryCards } from "./components/Cards.jsx";
import {
  TrendPanel,
  RecommendationsPanel,
  NLPDetailsPanel,
} from "./components/LayoutPanels.jsx";
import "./index.css";
import { callGemini } from "./services/geminiService";
import { validateInput } from "./utils/validation";
//const API_BASE = "http://localhost:8000";

export default function App() {
  const [text, setText] = useState("");
  const [city, setCity] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nlpFeatures, setNlpFeatures] = useState(null);
  const [mlFeatures, setMlFeatures] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [recommendations, setRecommendations] = useState(null);


  /*const handleAnalyze = async () => {
  setLoading(true);
  setError(null);

  try {
    const resp = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        city,
      }),
    });

    if (!resp.ok) throw new Error(`API error: ${resp.status}`);

    const raw = await resp.json();
    console.log("RAW API:", raw);


    const nlp_features = raw.nlp_features || null;

    const ml_features = {
    pollution_score: raw.pollution_risk,
    climate_score: raw.climate_risk,
    environmental_risk: raw.env_risk,
  };

  const predictions = {
    overall_risk_score: raw.risk_score,
    overall_risk_level:
      raw.final_risk >= 0.7
        ? "High"
        : raw.final_risk >= 0.4
        ? "Moderate"
        : "Low",
    primary_condition: raw.condition,
    disease_groups: raw.top_diseases || [],
  };

  Recommendations
    const recommendations = raw.recommendations || [];

    setNlpFeatures(nlp_features);
    setMlFeatures(ml_features);
    setPrediction(predictions);
    setRecommendations(recommendations);

  } catch (e) {
    console.error(e);
    setError("Failed to analyze. Ensure backend services are running.");
  } finally {
    setLoading(false);
  }
}*/

const handleAnalyze = async () => {
  setLoading(true);
  setError(null);

  try {
    // ✅ STEP 1: VALIDATE INPUT
    validateInput(city, text);

    // ✅ STEP 2: CALL GEMINI INSTEAD OF BACKEND
    const raw = await callGemini(city, text);

    console.log("GEMINI RAW:", raw);

    // ✅ STEP 3: HANDLE GEMINI ERROR RESPONSE
    if (raw.error) {
      throw new Error(raw.error);
    }

    /*-------------------------------
       ADAPTER: GEMINI → UI CONTRACT
    --------------------------------

    -------------------------------
   NEW: DIRECT GEMINI STRUCTURE
--------------------------------*/

// 🔴 Validate response
if (!raw.valid) {
  throw new Error(raw.errors?.join(", ") || "Invalid input");
}

// ✅ NLP Features (REAL)
setNlpFeatures(raw.nlp_features);

// ✅ ML Features (REAL)
setMlFeatures(raw.ml_features);

// ✅ Prediction (REAL)
setPrediction({
  overall_risk_score: raw.prediction.risk_score,
  overall_risk_level: raw.prediction.risk_level,
  primary_condition: raw.prediction.primary_condition,
  disease_groups: raw.prediction.disease_groups,
});

// ✅ Recommendations
setRecommendations(raw.recommendations);

    /*-------------------------------
       SET STATE (NO CHANGE)
    --------------------------------*/
    //setNlpFeatures(nlp_features);
    //etMlFeatures(ml_features);
    //setPrediction(predictions);
    //setRecommendations(recommendations);

  } catch (e) {
    console.error(e);
    setError(e.message || "Failed to analyze.");
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="min-h-screen flex bg-background text-tealDark">
      <Sidebar />
      <main className="flex-1 p-4 md:p-6">
       
        {/* ===== Dashboard Header ===== */}
        <header className="mb-6">
          <h1 className="text-2xl font-semibold text-navy mb-1">
            GeoHealth AI
          </h1>
          <p className="text-sm text-tealDark/70 mb-4">
            Health risk insights based on environment and personal context
          </p>

          {/* ===== Wide Input Bar ===== */}
          <Topbar
          onAnalyze={handleAnalyze}
          text={text}
          setText={setText}
          city={city}
          setCity={setCity}
          loading={loading}
        />
        </header>
        {error && (
          <div className="mb-3 text-xs bg-orangePrimary/10 text-orangePrimary px-3 py-2 rounded-xl">
            {error}
          </div>
        )}
        <SummaryCards prediction={prediction} nlp={nlpFeatures} />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="md:col-span-2">
            <TrendPanel mlFeatures={mlFeatures} />
          </div>
          <NLPDetailsPanel nlp={nlpFeatures} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <RecommendationsPanel recommendations={recommendations} />
          </div>
          <div className="bg-surface rounded-2xl shadow-sm p-4">
            <h2 className="text-sm font-semibold text-navy mb-2">
              Demo Instructions
            </h2>
            <p className="text-xs text-tealDark/80 mb-1">
               1. In the text box above, describe your age,health conditions, symptoms,
              lifestyle, or family history in simple words.
            </p>
            <p className="text-xs text-tealDark/80 mb-1">
              2. Enter the city where you currently live to assess environmental exposure.
            </p>
            <p className="text-xs text-tealDark/80">
               3. Click <span className="font-semibold">Run Analysis</span> to analyze
              health risk patterns influenced by environment and health context.
            </p>
            <p className="text-xs text-tealDark/80">
              4. Review the dashboard to understand environmental risk, extracted profile,
              and preventive recommendations.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
