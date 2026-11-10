import { useState } from "react";
import { Link } from "react-router-dom";
import { getFollowUps, updateFollowUp } from "../api/followups";
import { label } from "../i18n/labels";
import Badge     from "../components/ui/Badge";
import Button    from "../components/ui/Button";
import DataTable from "../components/ui/DataTable";

const STATUSES = ["Pending", "Completed", "Cancelled"];

export default function FollowUps() {
  const [status,    setStatus]    = useState("Pending");
  const [reloadKey, setReloadKey] = useState(0);

  async function markDone(id) {
    await updateFollowUp(id, { status: "Completed" });
    setReloadKey((k) => k + 1);
  }

  const columns = [
    { key: "scheduled_date", label: "Fecha", sortable: true },
    { key: "customer_name", label: "Cliente", sortable: true,
      render: (f) => (
        <Link to={`/customers/${f.customer_id}`} className="font-medium text-blue-600 hover:underline">
          {f.customer_name ?? `#${f.customer_id}`}
        </Link>
      ) },
    { key: "reason", label: "Motivo", sortable: true, render: (f) => (f.reason ? label(f.reason) : "—") },
    { key: "status", label: "Estado", sortable: true, render: (f) => <Badge value={f.status} /> },
    { key: "action", label: "Acción",
      render: (f) => f.status === "Pending" && (
        <Button variant="ghost" size="sm" onClick={() => markDone(f.id)}>✓ Completar</Button>
      ) },
  ];

  return (
    <DataTable
      title="Seguimientos"
      fetcher={getFollowUps}
      columns={columns}
      filters={{ status: status || undefined }}
      reloadKey={reloadKey}
      searchPlaceholder="Buscar por cliente o motivo..."
      defaultSort={{ key: "scheduled_date", dir: "asc" }}
      toolbar={
        <select value={status} onChange={(e) => setStatus(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm">
          <option value="">Todos los estados</option>
          {STATUSES.map((s) => <option key={s} value={s}>{label(s)}</option>)}
        </select>
      }
    />
  );
}
