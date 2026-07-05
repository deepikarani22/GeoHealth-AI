/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#EFEFEF",
        surface: "#FFFFFF",
        navy: "#012C5B",
        tealDark: "#0C3A46",
        bluePrimary: "#024EAD",
        blueLight: "#74AADB",
        greenPrimary: "#30A128",
        greenDark: "#47773A",
        greenLight: "#79C646",
        greenDeep: "#29482B",
        orangePrimary: "#FE6405",
        brownDark: "#46351d"
      }
    }
  },
  plugins: []
};
