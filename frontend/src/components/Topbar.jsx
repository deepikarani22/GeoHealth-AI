import React from "react";

export default function Topbar({
  onAnalyze,
  text,
  setText,
  city,
  setCity,
  loading,
}) {
  const isDisabled = loading || !text.trim() || !city.trim();

  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 mb-6">
      <div className="flex flex-col md:flex-row gap-3 items-stretch">
        <input
          type="text"
          className="flex-1 bg-background rounded-xl px-4 py-3 text-sm outline-none"
          placeholder="Describe your health, lifestyle, and environment..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <input
          type="text"
          className="w-full md:w-40 bg-background rounded-xl px-4 py-3 text-sm outline-none"
          placeholder="City"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />

        <button
          onClick={onAnalyze}
          disabled={isDisabled}
          className="px-6 py-3 rounded-xl text-sm font-medium bg-bluePrimary text-white hover:bg-blueLight disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>

      {(!text.trim() || !city.trim()) && (
        <p className="mt-2 text-[11px] text-tealDark/60">
          Please enter both a health description and city to run analysis.
        </p>
      )}
    </div>
  );
}



/*import React from "react";

export default function Topbar({ onAnalyze, text, setText, loading }) {
  return (
    <div className="bg-surface rounded-2xl shadow-sm p-4 mb-6">
      <div className="flex flex-col md:flex-row gap-3 items-stretch">
        <input
          type="text"
          className="flex-1 bg-background rounded-xl px-4 py-3 text-sm outline-none"
          placeholder="Describe your health, lifestyle, and environment..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={onAnalyze}
          disabled={loading || !text.trim()}
          className="px-6 py-3 rounded-xl text-sm font-medium bg-bluePrimary text-white hover:bg-blueLight disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>
    </div>
  );
}
*/



/*import React from "react";

export default function Topbar({ onAnalyze, text, setText, loading }) {
  return (
    <header className="flex items-center justify-between mb-4">
      <div>
        <h1 className="text-2xl font-semibold text-navy">Dashboard</h1>
        <p className="text-sm text-tealDark/70">
          End-to-end health risk analysis from free-text input.
        </p>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center bg-surface rounded-full px-4 py-2 shadow-sm">
          <span className="text-gray-400 mr-2">🔍</span>
          <input
            type="text"
            className="bg-transparent text-sm outline-none w-64"
            placeholder="Paste health description here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button
          onClick={onAnalyze}
          disabled={loading || !text.trim()}
          className="px-4 py-2 rounded-full text-sm font-medium bg-bluePrimary text-white hover:bg-blueLight disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
        <div className="w-9 h-9 rounded-full bg-blueLight flex items-center justify-center text-navy font-semibold">
          U
        </div>
      </div>
    </header>
  );
}*/
