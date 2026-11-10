import { useState } from "react";
import Button from "../ui/Button";
import { label } from "../../i18n/labels";

const OUTCOMES  = ["Interested", "Not interested", "No answer", "Busy", "Wrong number"];
const INTERESTS = ["High", "Medium", "Low", "No interest"];

export default function CallForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    outcome:  "Interested",
    interest: "Medium",
    requested_info:    false,
    accepted_followup: false,
    notes: "",
  });

  const set = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Resultado</label>
        <select value={form.outcome} onChange={(e) => set("outcome", e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none">
          {OUTCOMES.map((o) => <option key={o} value={o}>{label(o)}</option>)}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nivel de interés</label>
        <select value={form.interest} onChange={(e) => set("interest", e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none">
          {INTERESTS.map((i) => <option key={i} value={i}>{label(i)}</option>)}
        </select>
      </div>

      <div className="flex gap-6">
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input type="checkbox" checked={form.requested_info}
            onChange={(e) => set("requested_info", e.target.checked)}
            className="rounded text-blue-600" />
          Solicitó información
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input type="checkbox" checked={form.accepted_followup}
            onChange={(e) => set("accepted_followup", e.target.checked)}
            className="rounded text-blue-600" />
          Aceptó seguimiento
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notas</label>
        <textarea value={form.notes} onChange={(e) => set("notes", e.target.value)}
          rows={3} placeholder="Notas opcionales..."
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none resize-none" />
      </div>

      <Button variant="primary" size="lg" className="w-full" onClick={() => onSubmit(form)} disabled={loading}>
        {loading ? "Guardando..." : "💾 Guardar y obtener predicción"}
      </Button>
    </div>
  );
}

