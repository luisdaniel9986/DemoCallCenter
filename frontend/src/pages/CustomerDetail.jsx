import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Building2, Mail, Phone } from "lucide-react";
import { getCustomer }    from "../api/customers";
import { getCalls }       from "../api/calls";
import { getFollowUps }   from "../api/followups";
import { getPredictions } from "../api/predictions";
import { label }          from "../i18n/labels";
import { formatDuration } from "../utils/format";
import Badge              from "../components/ui/Badge";
import Card               from "../components/ui/Card";
import LoadingSpinner     from "../components/ui/LoadingSpinner";
import PredictionResult   from "../components/predictions/PredictionResult";

export default function CustomerDetail() {
  const { id } = useParams();
  const [customer,    setCustomer]    = useState(null);
  const [calls,       setCalls]       = useState([]);
  const [followups,   setFollowups]   = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [callsTotal,     setCallsTotal]     = useState(0);
  const [followupsTotal, setFollowupsTotal] = useState(0);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
    const params = { customer_id: id, page_size: 50 };
    Promise.all([getCustomer(id), getCalls(params), getFollowUps(params), getPredictions(params)])
      .then(([c, callsRes, f, p]) => {
        setCustomer(c.data);
        setCalls(callsRes.data.items); setCallsTotal(callsRes.data.total);
        setFollowups(f.data.items);    setFollowupsTotal(f.data.total);
        setPredictions(p.data.items);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner message="Cargando cliente..." />;
  if (error || !customer) return <Card><p className="text-gray-500">Cliente no encontrado.</p></Card>;

  return (
    <div className="space-y-6">
      <Link to="/customers" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800">
        <ArrowLeft size={14} /> Volver a clientes
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xl font-bold text-gray-800">{customer.name}</h2>
            <Badge value={customer.status} />
          </div>
          <div className="space-y-1.5 text-sm text-gray-600">
            <p className="flex items-center gap-2"><Building2 size={14} /> {customer.company || "—"}</p>
            <p className="flex items-center gap-2"><Phone size={14} /> <span className="font-mono">{customer.phone}</span></p>
            <p className="flex items-center gap-2"><Mail size={14} /> {customer.email || "—"}</p>
            <p className="text-gray-400">Edad: {customer.age ?? "—"} · Registrado: {customer.registered_at ?? "—"}</p>
          </div>
        </Card>
        {predictions[0]
          ? <PredictionResult prediction={predictions[0]} />
          : <Card className="text-center text-sm text-gray-400">Sin predicciones</Card>}
      </div>

      <Card>
        <h3 className="font-semibold text-gray-700 mb-3">Llamadas ({callsTotal}){callsTotal > calls.length ? ` · últimas ${calls.length}` : ""}</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b text-xs uppercase tracking-wide">
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Duración</th>
                <th className="pb-2 pr-4">Resultado</th>
                <th className="pb-2 pr-4">Interés</th>
                <th className="pb-2">Notas</th>
              </tr>
            </thead>
            <tbody>
              {calls.length === 0 && <tr><td colSpan={5} className="py-4 text-center text-gray-400">Sin llamadas</td></tr>}
              {calls.map((c) => (
                <tr key={c.id} className="border-b border-gray-50">
                  <td className="py-2 pr-4 text-gray-500 whitespace-nowrap">{new Date(c.called_at).toLocaleString("es-PE")}</td>
                  <td className="py-2 pr-4 font-mono text-gray-500">{formatDuration(c.duration_seconds)}</td>
                  <td className="py-2 pr-4 text-gray-700">{label(c.outcome)}</td>
                  <td className="py-2 pr-4 text-gray-500">{label(c.interest)}</td>
                  <td className="py-2 text-gray-400 text-xs">{c.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold text-gray-700 mb-3">Seguimientos ({followupsTotal}){followupsTotal > followups.length ? ` · primeros ${followups.length}` : ""}</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b text-xs uppercase tracking-wide">
              <th className="pb-2 pr-4">Fecha</th>
              <th className="pb-2 pr-4">Motivo</th>
              <th className="pb-2">Estado</th>
            </tr>
          </thead>
          <tbody>
            {followups.length === 0 && <tr><td colSpan={3} className="py-4 text-center text-gray-400">Sin seguimientos</td></tr>}
            {followups.map((f) => (
              <tr key={f.id} className="border-b border-gray-50">
                <td className="py-2 pr-4 text-gray-600">{f.scheduled_date}</td>
                <td className="py-2 pr-4 text-gray-500">{f.reason ? label(f.reason) : "—"}</td>
                <td className="py-2"><Badge value={f.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
