import Badge from "../ui/Badge";
import Card  from "../ui/Card";

export default function PendingFollowupsTable({ followups = [] }) {
  return (
    <Card>
      <h3 className="font-semibold text-gray-700 mb-3">Seguimientos pendientes (por prioridad ML)</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-100 text-xs uppercase tracking-wide">
              <th className="pb-2 pr-4">Cliente</th>
              <th className="pb-2 pr-4">Empresa</th>
              <th className="pb-2 pr-4">Fecha</th>
              <th className="pb-2 pr-4">Prioridad</th>
              <th className="pb-2">Probabilidad</th>
            </tr>
          </thead>
          <tbody>
            {followups.length === 0 && (
              <tr><td colSpan={5} className="py-6 text-center text-gray-400">No hay seguimientos pendientes</td></tr>
            )}
            {followups.map((f, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 pr-4 font-medium text-gray-800">{f.customer_name}</td>
                <td className="py-2 pr-4 text-gray-500">{f.company || "—"}</td>
                <td className="py-2 pr-4 text-gray-500">{f.scheduled_date}</td>
                <td className="py-2 pr-4"><Badge value={f.ml_priority} priority /></td>
                <td className="py-2 font-semibold text-blue-600">
                  {f.probability != null ? `${(f.probability * 100).toFixed(0)}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

