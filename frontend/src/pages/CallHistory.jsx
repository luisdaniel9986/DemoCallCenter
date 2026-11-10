import { useState } from "react";
import { Link } from "react-router-dom";
import { getCalls } from "../api/calls";
import { label } from "../i18n/labels";
import { formatDuration } from "../utils/format";
import DataTable from "../components/ui/DataTable";

const OUTCOMES = ["Interested", "Not interested", "No answer", "Busy", "Wrong number"];

const COLUMNS = [
  { key: "called_at", label: "Fecha", sortable: true,
    render: (c) => <span className="whitespace-nowrap">{c.called_at ? new Date(c.called_at).toLocaleString("es-PE") : "—"}</span> },
  { key: "customer_name", label: "Cliente", sortable: true,
    render: (c) => (
      <Link to={`/customers/${c.customer_id}`} className="font-medium text-blue-600 hover:underline">
        {c.customer_name ?? `#${c.customer_id}`}
      </Link>
    ) },
  { key: "duration_seconds", label: "Duración", sortable: true,
    render: (c) => <span className="font-mono">{formatDuration(c.duration_seconds)}</span> },
  { key: "outcome",  label: "Resultado", sortable: true, render: (c) => label(c.outcome) },
  { key: "interest", label: "Interés",   sortable: true, render: (c) => label(c.interest) },
  { key: "requested_info",    label: "Info",        render: (c) => (c.requested_info ? "Sí" : "No") },
  { key: "accepted_followup", label: "Seguimiento", render: (c) => (c.accepted_followup ? "Sí" : "No") },
  { key: "notes", label: "Notas", render: (c) => <span className="text-xs text-gray-400">{c.notes || "—"}</span> },
];

export default function CallHistory() {
  const [outcome, setOutcome] = useState("");

  return (
    <DataTable
      title="Historial de llamadas"
      fetcher={getCalls}
      columns={COLUMNS}
      filters={{ outcome: outcome || undefined }}
      searchPlaceholder="Buscar por cliente o notas..."
      defaultSort={{ key: "called_at", dir: "desc" }}
      toolbar={
        <select value={outcome} onChange={(e) => setOutcome(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm">
          <option value="">Todos los resultados</option>
          {OUTCOMES.map((o) => <option key={o} value={o}>{label(o)}</option>)}
        </select>
      }
    />
  );
}
