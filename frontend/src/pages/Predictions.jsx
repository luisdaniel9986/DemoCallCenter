import { useState } from "react";
import { Link } from "react-router-dom";
import { getPredictions } from "../api/predictions";
import { label, priorityLabel } from "../i18n/labels";
import Badge     from "../components/ui/Badge";
import DataTable from "../components/ui/DataTable";

const CLASSES = ["High", "Medium", "Low"];

const COLUMNS = [
  { key: "customer_name", label: "Cliente", sortable: true,
    render: (p) => (
      <Link to={`/customers/${p.customer_id}`} className="font-medium text-blue-600 hover:underline">
        {p.customer_name ?? `#${p.customer_id}`}
      </Link>
    ) },
  { key: "probability", label: "Probabilidad", sortable: true,
    render: (p) => <span className="font-bold text-blue-600">{Math.round(p.probability * 100)}%</span> },
  { key: "classification", label: "Prioridad", sortable: true,
    render: (p) => <Badge value={p.classification} priority /> },
  { key: "recommendation", label: "Recomendación",
    render: (p) => <span className="text-xs text-gray-500">{label(p.recommendation)}</span> },
  { key: "predicted_at", label: "Fecha", sortable: true,
    render: (p) => <span className="text-xs text-gray-400">{p.predicted_at ? new Date(p.predicted_at).toLocaleDateString("es-PE") : "—"}</span> },
];

export default function Predictions() {
  const [classification, setClassification] = useState("");

  return (
    <DataTable
      title="Predicciones ML"
      fetcher={getPredictions}
      columns={COLUMNS}
      filters={{ classification: classification || undefined }}
      searchPlaceholder="Buscar por cliente o recomendación..."
      defaultSort={{ key: "predicted_at", dir: "desc" }}
      toolbar={
        <select value={classification} onChange={(e) => setClassification(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm">
          <option value="">Todas las prioridades</option>
          {CLASSES.map((c) => <option key={c} value={c}>{priorityLabel(c)}</option>)}
        </select>
      }
    />
  );
}
