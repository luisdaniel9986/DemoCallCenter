import { useState } from "react";
import { Link } from "react-router-dom";
import { getCustomers } from "../api/customers";
import { label } from "../i18n/labels";
import Badge     from "../components/ui/Badge";
import DataTable from "../components/ui/DataTable";

const STATUSES = ["New", "Active", "Inactive", "VIP"];

const COLUMNS = [
  { key: "name", label: "Nombre", sortable: true,
    render: (c) => (
      <Link to={`/customers/${c.id}`} className="font-medium text-blue-600 hover:underline">{c.name}</Link>
    ) },
  { key: "company", label: "Empresa", sortable: true, render: (c) => c.company || "—" },
  { key: "phone",   label: "Teléfono", render: (c) => <span className="font-mono">{c.phone}</span> },
  { key: "email",   label: "Correo", render: (c) => c.email || "—" },
  { key: "age",     label: "Edad", sortable: true, render: (c) => c.age ?? "—" },
  { key: "status",  label: "Estado", sortable: true, render: (c) => <Badge value={c.status} /> },
];

export default function Customers() {
  const [status, setStatus] = useState("");

  return (
    <DataTable
      title="Clientes"
      fetcher={getCustomers}
      columns={COLUMNS}
      filters={{ status: status || undefined }}
      searchPlaceholder="Buscar por nombre, empresa, correo o teléfono..."
      defaultSort={{ key: "name", dir: "asc" }}
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
