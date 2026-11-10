import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { label, priorityLabel } from "../../i18n/labels";

const COLORS = ["#2563eb", "#16a34a", "#eab308", "#dc2626", "#9333ea", "#0891b2"];
const CLASS_COLORS = { High: "#16a34a", Medium: "#eab308", Low: "#dc2626" };

function ChartCard({ title, children }) {
  return (
    <Card>
      <h3 className="font-semibold text-gray-700 mb-3">{title}</h3>
      <div className="h-64">{children}</div>
    </Card>
  );
}

function DonutChart({ data, colorFor, translate }) {
  const rows = data.map((d) => ({ ...d, label: translate(d.name) }));
  return (
    <ResponsiveContainer>
      <PieChart>
        <Pie data={rows} dataKey="total" nameKey="label" innerRadius={50} outerRadius={85} paddingAngle={2} label>
          {rows.map((d, i) => <Cell key={d.name} fill={colorFor(d.name, i)} />)}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

export default function DashboardCharts({ data }) {
  const { callsPerDay, outcomes, byStatus, byClass, distribution, priority } = data;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard title="Llamadas por día">
          <ResponsiveContainer>
            <LineChart data={callsPerDay}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="total" name="Llamadas" stroke="#2563eb" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Resultados de llamadas">
          <DonutChart data={outcomes} translate={label} colorFor={(_, i) => COLORS[i % COLORS.length]} />
        </ChartCard>

        <ChartCard title="Clientes por estado">
          <DonutChart data={byStatus} translate={label} colorFor={(_, i) => COLORS[i % COLORS.length]} />
        </ChartCard>

        <ChartCard title="Predicciones por prioridad">
          <DonutChart data={byClass} translate={priorityLabel} colorFor={(n) => CLASS_COLORS[n] ?? "#9ca3af"} />
        </ChartCard>
      </div>

      <ChartCard title="Distribución de la probabilidad de conversión">
        <ResponsiveContainer>
          <BarChart data={distribution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis dataKey="range" tick={{ fontSize: 11 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="total" name="Predicciones" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <Card>
        <h3 className="font-semibold text-gray-700 mb-3">Clientes prioritarios</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b text-xs uppercase tracking-wide">
              <th className="pb-2 pr-4">Cliente</th>
              <th className="pb-2 pr-4">Empresa</th>
              <th className="pb-2 pr-4">Prioridad</th>
              <th className="pb-2">Probabilidad</th>
            </tr>
          </thead>
          <tbody>
            {priority.map((c) => (
              <tr key={c.id} className="border-b border-gray-50">
                <td className="py-2 pr-4 font-medium text-gray-800">{c.name}</td>
                <td className="py-2 pr-4 text-gray-500">{c.company || "—"}</td>
                <td className="py-2 pr-4"><Badge value={c.classification} priority /></td>
                <td className="py-2 font-semibold text-blue-600">{Math.round(c.probability * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
