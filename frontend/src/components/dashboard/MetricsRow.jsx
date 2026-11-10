import StatCard from "../ui/StatCard";
import { Phone, CheckCircle, CalendarCheck, Users, BrainCircuit } from "lucide-react";

export default function MetricsRow({ metrics }) {
  if (!metrics) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
      <StatCard label="Llamadas"          value={metrics.total_calls}          icon={Phone}          color="blue"   />
      <StatCard label="Atendidas"         value={metrics.answered_calls}       icon={CheckCircle}    color="green"  />
      <StatCard label="Seguimientos pendientes" value={metrics.pending_followups} icon={CalendarCheck}  color="yellow" />
      <StatCard label="Clientes"          value={metrics.total_customers}           icon={Users}          color="purple" />
      <StatCard label="Prioridad ML alta" value={metrics.high_predictions}        icon={BrainCircuit}   color="red"    />
    </div>
  );
}

