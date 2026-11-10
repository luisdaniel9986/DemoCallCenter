import Badge from "../ui/Badge";
import Card  from "../ui/Card";
import { BrainCircuit } from "lucide-react";
import { label } from "../../i18n/labels";

export default function PredictionResult({ prediction }) {
  if (!prediction) return null;

  const pct  = Math.round(prediction.probability * 100);
  const color = pct >= 65 ? "text-green-600" : pct >= 35 ? "text-yellow-600" : "text-red-500";

  return (
    <Card className="text-center">
      <div className="flex items-center justify-center gap-2 mb-3 text-blue-600">
        <BrainCircuit size={20} />
        <span className="font-semibold">Análisis predictivo</span>
      </div>
      <p className="text-sm text-gray-500 mb-1">Probabilidad de conversión</p>
      <p className={`text-5xl font-black mb-2 ${color}`}>{pct}%</p>
      <div className="flex justify-center mb-3">
        <Badge value={prediction.classification} priority />
      </div>
      <p className="text-sm text-gray-600 font-medium">{label(prediction.recommendation)}</p>
    </Card>
  );
}

