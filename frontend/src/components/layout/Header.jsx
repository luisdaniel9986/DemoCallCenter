import { useLocation } from "react-router-dom";

const TITLES = {
  "/":            "Dashboard",
  "/call-center": "Call Center",
  "/customers":   "Clientes",
  "/calls":       "Historial de llamadas",
  "/followups":   "Seguimientos",
  "/predictions": "Predicciones",
};

export default function Header() {
  const { pathname } = useLocation();
  const title = TITLES[pathname]
    ?? (pathname.startsWith("/customers/") ? "Detalle del cliente" : "Call Center CRM");
  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
      <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
      <span className="text-xs text-gray-400">
        {new Date().toLocaleDateString("es-PE", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
      </span>
    </header>
  );
}

