import { Phone, Building2 } from "lucide-react";
import Button from "../ui/Button";

export default function IncomingCallCard({ callData, onAnswer, onReject }) {
  if (!callData) return null;
  return (
    <div className="bg-gray-900 text-white rounded-2xl p-6 max-w-sm mx-auto text-center shadow-2xl">
      <div className="animate-pulse mb-4">
        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto">
          <Phone size={28} />
        </div>
      </div>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-1">Llamada entrante</p>
      <h2 className="text-2xl font-bold mb-1">{callData.name}</h2>
      <p className="text-gray-400 text-sm flex items-center justify-center gap-1">
        <Building2 size={13} /> {callData.company}
      </p>
      <p className="text-gray-300 text-lg font-mono mt-1">{callData.phone}</p>

      <div className="flex gap-3 mt-6 justify-center">
        <Button variant="danger"   size="lg" onClick={onReject}>🔴 Rechazar</Button>
        <Button variant="success"  size="lg" onClick={onAnswer}>🟢 Contestar</Button>
      </div>
    </div>
  );
}

