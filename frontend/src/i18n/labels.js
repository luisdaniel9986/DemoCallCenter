// UI labels (Spanish, shown to end users) for the English values stored in the API/DB.
// Code and data stay in English; only what the user reads is translated here.

const LABELS = {
  // customer status
  New: "Nuevo", Active: "Activo", Inactive: "Inactivo", VIP: "VIP",
  // call outcome
  Interested: "Interesado", "Not interested": "No interesado", "No answer": "Sin respuesta",
  Busy: "Ocupado", "Wrong number": "Número incorrecto",
  // interest level
  High: "Alto", Medium: "Medio", Low: "Bajo", "No interest": "Ninguno",
  // follow-up status
  Pending: "Pendiente", Completed: "Completado", Cancelled: "Cancelado",
  // ML recommendations / follow-up reasons
  "Prioritize immediate follow-up": "Priorizar seguimiento inmediato",
  "Schedule follow-up in 7 days": "Programar seguimiento en 7 días",
  "Do not prioritize in this campaign": "No priorizar en esta campaña",
  "Commercial follow-up": "Seguimiento comercial",
  "Proposal delivery": "Envío de propuesta",
  "Technical inquiry": "Consulta técnica",
  "Deal closing": "Cierre de venta",
  "Satisfaction check": "Verificación de satisfacción",
};

// Priority labels differ in gender from interest levels (Alta/Media/Baja).
const PRIORITY = { High: "Alta", Medium: "Media", Low: "Baja" };

export const label = (value) => LABELS[value] ?? value;
export const priorityLabel = (value) => PRIORITY[value] ?? value;
