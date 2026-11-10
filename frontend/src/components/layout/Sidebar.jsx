import { NavLink } from "react-router-dom";
import { LayoutDashboard, Phone, Users, CalendarCheck, BrainCircuit, History } from "lucide-react";

const NAV = [
  { to: "/",           label: "Dashboard",   icon: LayoutDashboard },
  { to: "/call-center",label: "Call Center", icon: Phone },
  { to: "/customers",  label: "Clientes",     icon: Users },
  { to: "/calls",      label: "Historial",     icon: History },
  { to: "/followups",  label: "Seguimientos", icon: CalendarCheck },
  { to: "/predictions",label: "Predicciones", icon: BrainCircuit },
];

export default function Sidebar() {
  return (
    <aside className="w-60 min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <div className="px-6 py-5 border-b border-gray-700">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Call Center</p>
        <h1 className="text-lg font-bold text-white mt-0.5">CRM · ML</h1>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
               ${isActive ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"}`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-gray-700 text-xs text-gray-500">
        Backend · http://localhost:8000
      </div>
    </aside>
  );
}

