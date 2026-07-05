import React from "react";

const navItems = [
  { label: "Overview", icon: "👁" }
];

/*const navItems = [
  { label: "Overview", icon: "👁" },
  { label: "Analysis", icon: "📊" },
  { label: "Patients", icon: "👤" },
  { label: "Reports", icon: "📑" },
  { label: "Settings", icon: "⚙️" },
  { label: "Developer", icon: "💻" },
];*/

export default function Sidebar() {
  return (
    <aside className="w-60 bg-navy text-white flex flex-col">
      <div className="px-6 py-5 flex items-center gap-2 border-b border-blueLight/20">
        <div className="w-9 h-9 rounded-full bg-bluePrimary flex items-center justify-center text-white font-bold">
          G
        </div>
        <div className="flex flex-col leading-tight">
          <span className="font-semibold text-lg">GeoHealthAI</span>
          <span className="text-xs text-blueLight/80">Risk Dashboard</span>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.label}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm hover:bg-bluePrimary/70 transition"
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}


/*export default function Sidebar() {
  return (
    <aside className="w-60 bg-navy text-white flex flex-col">
      <div className="px-6 py-5 flex items-center gap-2 border-b border-blueLight/20">
        <div className="w-9 h-9 rounded-full bg-bluePrimary flex items-center justify-center text-white font-bold">
          G
        </div>
        <div className="flex flex-col leading-tight">
          <span className="font-semibold text-lg">GeoHealthAI</span>
          <span className="text-xs text-blueLight/80">Risk Dashboard</span>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.label}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm hover:bg-bluePrimary/70 transition"
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <button className="m-4 mt-auto flex items-center gap-2 px-3 py-2 rounded-xl text-sm bg-bluePrimary/30 hover:bg-bluePrimary/60 transition">
        <span>⎋</span>
        <span>Log out</span>
      </button>
    </aside>
  );
}*/
