import React from "react";


export function TrendPanel({ mlFeatures }) {
  if (!mlFeatures) {
    return (
      <div className="bg-surface rounded-2xl shadow-sm p-4 text-xs text-tealDark/70">
        Run an analysis to see environmental risk factors.
      </div>
    );
  }

  const items = [
    { label: "Air Pollution", value: mlFeatures.pollution_score },
    { label: "Climate Stress", value: mlFeatures.climate_score },
    { label: "Environmental Risk", value: mlFeatures.environmental_risk },
  ];

  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">Environmental Risk Factors</h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-tealDark/10 text-tealDark">
          Model-derived
        </span>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <div className="w-40 text-xs text-tealDark/80">{item.label}</div>
            <div className="flex-1 bg-background rounded-full h-2 overflow-hidden">
              <div
                className="h-full rounded-full bg-bluePrimary transition-all"
                style={{ width: `${Math.round(item.value * 100)}%` }}
              />
            </div>
            <span className="text-xs text-tealDark/70">
              {(item.value * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/*export function TrendPanel({ mlFeatures }) {
  const items = [
    { label: "Smoking", value: mlFeatures?.smoking ?? 0 },
    { label: "Poor diet", value: mlFeatures?.poor_diet ?? 0 },
    { label: "No exercise", value: mlFeatures?.exercise_none ?? 0 },
    { label: "Pollution (high)", value: mlFeatures?.pollution_high ?? 0 },
    {
      label: "Family history",
      value: mlFeatures?.family_history_respiratory ?? 0,
    },
  ];
  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">Risk Factors</h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-tealDark/10 text-tealDark">
          Feature contribution (binary)
        </span>
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <div className="w-32 text-xs text-tealDark/80">{item.label}</div>
            <div className="flex-1 bg-background rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  item.value ? "bg-bluePrimary" : "bg-gray-300"
                }`}
                style={{ width: item.value ? "80%" : "20%" }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}*/

export function RecommendationsPanel({ recommendations }) {
  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">
          Personalized Recommendations
        </h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-greenLight/10 text-greenDeep">
          Generated from risk profile
        </span>
      </div>
      {(!recommendations || recommendations.length === 0) && (
        <p className="text-xs text-tealDark/70">
          Run an analysis to see tailored recommendations here.
        </p>
      )}
      <ul className="space-y-2 text-sm">
        {Array.isArray(recommendations) && recommendations?.map((rec, idx) => (
          <li
            key={idx}
            className="flex items-start gap-2 bg-background rounded-xl px-3 py-2"
          >
            <span className="mt-0.5 text-greenPrimary">●</span>
            <p className="text-tealDark text-xs md:text-sm">{rec}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function NLPDetailsPanel({ nlp }) {
  if (!nlp) {
    return (
      <div className="bg-surface rounded-2xl shadow-sm p-4 text-xs text-tealDark/70">
        No profile extracted yet. Run an analysis first.
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">Extracted Profile</h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blueLight/10 text-bluePrimary">
          From NLP layer
        </span>
      </div>

      <div className="space-y-2 text-xs md:text-sm text-tealDark">
        <p>
          <span className="font-medium">Age:</span>{" "}
          {nlp.age ?? "Not detected"}
        </p>

        <p>
          <span className="font-medium">Conditions:</span>{" "}
          {nlp.conditions?.length ? nlp.conditions.join(", ") : "None detected"}
        </p>

        <p>
          <span className="font-medium">Family history:</span>{" "}
          {nlp.family_history?.length
            ? nlp.family_history.join(", ")
            : "None reported"}
        </p>

        <p>
          <span className="font-medium">Pollution context:</span>{" "}
          {nlp.pollution?.severity
            ? `${nlp.pollution.environment} (${nlp.pollution.severity})`
            : "Not detected"}
        </p>

        <p className="text-[11px] text-tealDark/60">
          Raw entities:{" "}
          {nlp.raw_entities?.length
            ? nlp.raw_entities.join(", ")
            : "—"}
        </p>
      </div>
    </div>
  );
}


/*export function NLPDetailsPanel({ nlp }) {
  if (!nlp) {
    return (
      <div className="bg-surface rounded-2xl shadow-sm p-4 text-xs text-tealDark/70">
        No profile extracted yet. Run an analysis first.
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">Extracted Profile</h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blueLight/10 text-bluePrimary">
          From NLP layer
        </span>
      </div>

      <div className="space-y-2 text-xs md:text-sm text-tealDark">
        <p>
          <span className="font-medium">Age:</span>{" "}
          {nlp.age ?? "Not detected"}
        </p>

        <p>
          <span className="font-medium">Symptoms:</span>{" "}
          {nlp.symptoms?.length ? nlp.symptoms.join(", ") : "None detected"}
        </p>

        <p>
          <span className="font-medium">Inferred Condition:</span>{" "}
          {nlp.inferred_condition ?? "—"}
        </p>
      </div>
    </div>
  );
}*/

/*export function NLPDetailsPanel({ nlp }) {
  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 h-full">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-navy">Extracted Profile</h2>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blueLight/10 text-bluePrimary">
          From NLP layer
        </span>
      </div>
      {!nlp && (
        <p className="text-xs text-tealDark/70">
          No profile extracted yet. Run an analysis first.
        </p>
      )}
      {nlp && (
        <div className="space-y-2 text-xs md:text-sm text-tealDark">
          <p>
            <span className="font-medium">Age:</span>{" "}
            {nlp.age || "Not detected"}
          </p>
          <p>
            <span className="font-medium">Conditions:</span>{" "}
            {nlp.conditions.length ? nlp.conditions.join(", ") : "None"}
          </p>
          <p>
            <span className="font-medium">Lifestyle:</span>{" "}
            {nlp.lifestyle.smoking ? "Smoking · " : ""}
            {nlp.lifestyle.diet && `Diet: ${nlp.lifestyle.diet} · `}
            {nlp.lifestyle.exercise_level &&
              `Exercise: ${nlp.lifestyle.exercise_level}`}
          </p>
          <p>
            <span className="font-medium">Pollution:</span>{" "}
            {nlp.pollution.environment} ({nlp.pollution.severity})
          </p>
          <p>
            <span className="font-medium">Family history:</span>{" "}
            {nlp.family_history.length
              ? nlp.family_history.join(", ")
              : "None reported"}
          </p>
          <p className="text-[11px] text-tealDark/60">
            Raw entities: {nlp.raw_entities.join(", ") || "—"}
          </p>
        </div>
      )}
    </div>
  );
}*/
