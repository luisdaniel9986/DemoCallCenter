import { useEffect, useState } from "react";

export default function CallTimer({ running }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (!running) { setSeconds(0); return; }
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [running]);

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  return (
    <div className="text-center">
      <span className="text-4xl font-mono font-bold text-green-400">{mm}:{ss}</span>
      <p className="text-xs text-gray-400 mt-1">Llamada en curso</p>
    </div>
  );
}

// expose seconds so parent can capture call duration
export function useCallDuration(running) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [running]);
  return seconds;
}

