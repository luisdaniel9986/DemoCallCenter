import { useState } from "react";
import { simulateCall }   from "../api/calls";
import { registerCall }   from "../api/calls";
import { createPrediction } from "../api/predictions";
import IncomingCallCard   from "../components/calls/IncomingCallCard";
import CallTimer, { useCallDuration } from "../components/calls/CallTimer";
import CallForm           from "../components/calls/CallForm";
import PredictionResult   from "../components/predictions/PredictionResult";
import Button             from "../components/ui/Button";
import Card               from "../components/ui/Card";
import { Phone }          from "lucide-react";

// Call Center state machine: idle → ringing → active → wrap-up → done
const STATES = { IDLE: "idle", RINGING: "ringing", ACTIVE: "active", WRAPUP: "wrapup", DONE: "done" };

export default function CallCenter() {
  const [phase,       setPhase]      = useState(STATES.IDLE);
  const [callData,    setCallData]   = useState(null);
  const [prediction,  setPrediction] = useState(null);
  const [loading,     setLoading]    = useState(false);

  const duration = useCallDuration(phase === STATES.ACTIVE);

  async function handleSimulate() {
    setLoading(true);
    try {
      const { data } = await simulateCall({});
      setCallData(data);
      setPhase(STATES.RINGING);
    } finally { setLoading(false); }
  }

  function handleAnswer()  { setPhase(STATES.ACTIVE); }
  function handleReject()  { setPhase(STATES.IDLE); setCallData(null); }
  function handleHangUp()  { setPhase(STATES.WRAPUP); }

  async function handleSaveCall(formData) {
    setLoading(true);
    try {
      const { data: call } = await registerCall({
        customer_id:       callData.customer_id,
        duration_seconds:  duration,
        outcome:           formData.outcome,
        interest:          formData.interest,
        requested_info:    formData.requested_info,
        accepted_followup: formData.accepted_followup,
        notes:             formData.notes,
      });

      const { data: pred } = await createPrediction({
        customer_id:       callData.customer_id,
        call_id:           call.id,
        duration_seconds:  duration,
        outcome:           formData.outcome,
        interest:          formData.interest,
        requested_info:    formData.requested_info,
        accepted_followup: formData.accepted_followup,
        age:               callData.age || 30,
        customer_status:   callData.status || "New",
        has_followup:      formData.accepted_followup,
      });
      setPrediction(pred);
      setPhase(STATES.DONE);
    } finally { setLoading(false); }
  }

  function handleReset() {
    setPhase(STATES.IDLE); setCallData(null);
    setPrediction(null);
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">

      {/* IDLE */}
      {phase === STATES.IDLE && (
        <Card className="text-center py-10">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <Phone size={36} className="text-blue-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Call Center</h2>
          <p className="text-gray-500 text-sm mb-6">Presiona el botón para simular una llamada entrante</p>
          <Button variant="primary" size="lg" onClick={handleSimulate} disabled={loading}>
            📞 Simular llamada
          </Button>
        </Card>
      )}

      {/* RINGING */}
      {phase === STATES.RINGING && (
        <IncomingCallCard callData={callData} onAnswer={handleAnswer} onReject={handleReject} />
      )}

      {/* ACTIVE */}
      {phase === STATES.ACTIVE && (
        <Card>
          <div className="text-center mb-6">
            <p className="text-sm font-medium text-gray-500">En llamada con</p>
            <h3 className="text-xl font-bold text-gray-800">{callData?.name}</h3>
            <p className="text-gray-400 text-sm">{callData?.company} · {callData?.phone}</p>
          </div>
          <CallTimer running />
          <div className="mt-6 text-center">
            <Button variant="danger" size="lg" onClick={handleHangUp}>🔴 Finalizar</Button>
          </div>
        </Card>
      )}

      {/* WRAP-UP */}
      {phase === STATES.WRAPUP && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-800 mb-1">Registrar resultado de la llamada</h3>
          <p className="text-sm text-gray-400 mb-4">
            {callData?.name} · {duration}s · {callData?.phone}
          </p>
          <CallForm onSubmit={handleSaveCall} loading={loading} />
        </Card>
      )}

      {/* DONE */}
      {phase === STATES.DONE && (
        <div className="space-y-4">
          <PredictionResult prediction={prediction} />
          {prediction?.classification !== "Low" && (
            <Card className="bg-green-50 border-green-200">
              <p className="text-sm font-semibold text-green-700">
                ✅ Seguimiento creado automáticamente según la clasificación del modelo
              </p>
            </Card>
          )}
          <div className="text-center">
            <Button variant="ghost" onClick={handleReset}>← Nueva llamada</Button>
          </div>
        </div>
      )}

    </div>
  );
}

