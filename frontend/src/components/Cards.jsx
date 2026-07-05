import React from "react";

/*export function SummaryCards({ prediction, nlp }) {
  const risk = prediction?.risk_score ?? null;
  let riskLabel = "Not analyzed";
  let riskColor = "bg-gray-200 text-gray-700";
  if (risk !== null) {
    if (risk >= 0.8) {
      riskLabel = "High risk";
      riskColor = "bg-orangePrimary/10 text-orangePrimary";
    } else if (risk >= 0.5) {
      riskLabel = "Moderate risk";
      riskColor = "bg-greenDark/10 text-greenDark";
    } else {
      riskLabel = "Low risk";
      riskColor = "bg-greenPrimary/10 text-greenPrimary";
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <Card
        title="Risk Score"
        value={risk !== null ? (risk * 100).toFixed(0) + "%" : "--"}
        pill={riskLabel}
        pillClass={riskColor}
      />
      <Card
        title="Detected Conditions"
        value={nlp?.conditions?.length ?? 0}
        pill={(nlp?.conditions || []).join(", ") || "None"}
        pillClass="bg-blueLight/10 text-bluePrimary"
      />
      <Card
        title="Lifestyle Flags"
        value={[
          nlp?.lifestyle?.smoking ? "Smoking" : null,
          nlp?.lifestyle?.diet === "poor" ? "Poor diet" : null,
          nlp?.lifestyle?.exercise_level === "none" ? "No exercise" : null,
        ]
          .filter(Boolean)
          .length}
        pill="Smoking · Diet · Exercise"
        pillClass="bg-greenLight/10 text-greenDeep"
      />
      <Card
        title="Pollution Level"
        value={
          nlp?.pollution?.severity
            ? nlp.pollution.severity[0].toUpperCase() +
              nlp.pollution.severity.slice(1)
            : "--"
        }
        pill={nlp?.pollution?.environment || "Unknown environment"}
        pillClass="bg-bluePrimary/10 text-bluePrimary"
      />
    </div>
  );
}*/

export function SummaryCards({ prediction, nlp }) {
  const risk = prediction?.overall_risk_score ?? null;

  let riskLabel = "Not analyzed";
  let riskColor = "bg-gray-200 text-gray-700";

  if (risk !== null) {
    if (risk >= 0.7) {
      riskLabel = "High risk";
      riskColor = "bg-orangePrimary/10 text-orangePrimary";
    } else if (risk >= 0.4) {
      riskLabel = "Moderate risk";
      riskColor = "bg-greenDark/10 text-greenDark";
    } else {
      riskLabel = "Low risk";
      riskColor = "bg-greenPrimary/10 text-greenPrimary";
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <Card
        title="Risk Score"
        value={risk !== null ? `${Math.round(risk * 100)}%` : "--"}
        pill={riskLabel}
        pillClass={riskColor}
      />

      <Card
        title="Primary Condition"
        value={prediction?.primary_condition || "--"}
        pill="Model inference"
        pillClass="bg-blueLight/10 text-bluePrimary"
      />

      <Card
        title="Detected Conditions"
        value={nlp?.conditions?.length || 0}
        pill={nlp?.conditions?.join(", ") || "None"}
        pillClass="bg-greenLight/10 text-greenDeep"
      />

      <Card
        title="Environment"
        value="Urban"
        pill={nlp?.pollution?.severity || "Not detected"}
        pillClass="bg-bluePrimary/10 text-bluePrimary"
      />
    </div>
  );
}


function Card({ title, value, pill, pillClass }) {
  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs uppercase tracking-wide text-tealDark/70">
          {title}
        </p>
        <span
          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${pillClass}`}
        >
          {pill}
        </span>
      </div>
      <p className="text-2xl font-semibold text-navy">{value}</p>
    </div>
  );
}
