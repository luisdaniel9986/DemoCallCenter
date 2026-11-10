import { label as t, priorityLabel } from "../../i18n/labels";

// Status / classification badge. `value` is the English API value; the text shown is Spanish.
const STYLES = {
  High:        "bg-green-100 text-green-700",
  Medium:      "bg-yellow-100 text-yellow-700",
  Low:         "bg-red-100 text-red-700",
  Pending:     "bg-blue-100 text-blue-700",
  Completed:   "bg-green-100 text-green-700",
  Cancelled:   "bg-gray-100 text-gray-500",
  Active:      "bg-green-100 text-green-700",
  New:         "bg-blue-100 text-blue-700",
  Inactive:    "bg-gray-100 text-gray-500",
  VIP:         "bg-purple-100 text-purple-700",
};

export default function Badge({ value, priority = false }) {
  const style = STYLES[value] ?? "bg-gray-100 text-gray-600";
  const text  = value ? (priority ? priorityLabel(value) : t(value)) : "—";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${style}`}>
      {text}
    </span>
  );
}
