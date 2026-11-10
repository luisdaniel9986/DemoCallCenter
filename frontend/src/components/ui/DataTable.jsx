import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import Card from "./Card";

const PAGE_SIZES = [10, 25, 50, 100];

// Window of page numbers with gaps: 1 … 4 5 [6] 7 8 … 40
function pageWindow(current, total) {
  const pages = new Set([1, total, current - 1, current, current + 1]);
  const sorted = [...pages].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
  const out = [];
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) out.push("gap-" + p);
    out.push(p);
  });
  return out;
}

/**
 * Server-side data table (DataTables style).
 * Every search / sort / page change triggers a request; the backend applies
 * LIMIT/OFFSET so only the visible page is transferred.
 *
 * Props
 *  - fetcher(params) -> axios promise resolving to { data: { items, total, page, page_size, pages } }
 *  - columns: [{ key, label, sortable?, render?(row), className? }]   (key = backend sort name)
 *  - filters: extra query params (e.g. { outcome: "Busy" }); changing them goes back to page 1
 *  - toolbar: extra controls rendered next to the search box
 *  - reloadKey: change it to force a refetch (e.g. after an action on a row)
 */
export default function DataTable({
  title,
  fetcher,
  columns,
  filters = {},
  toolbar = null,
  searchPlaceholder = "Buscar...",
  defaultSort = null,
  defaultPageSize = 25,
  reloadKey = 0,
  rowKey = "id",
  emptyMessage = "No hay registros",
}) {
  const [searchInput, setSearchInput] = useState("");
  const [search,      setSearch]      = useState("");
  const [sort,        setSort]        = useState(defaultSort);   // { key, dir } | null
  const [pageSize,    setPageSize]    = useState(defaultPageSize);
  const [pageState,   setPageState]   = useState({ key: "", page: 1 });
  const [result,      setResult]      = useState({ key: "", data: null, error: false });

  // Debounce the search box so we don't query on every keystroke
  useEffect(() => {
    const timer = setTimeout(() => setSearch(searchInput.trim()), 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Anything that changes the result set resets the page to 1 (derived, no effect needed)
  const queryKey = JSON.stringify({ search, sort, pageSize, filters });
  const page     = pageState.key === queryKey ? pageState.page : 1;
  const goTo     = (p) => setPageState({ key: queryKey, page: p });

  const requestKey = `${queryKey}|${page}|${reloadKey}`;

  useEffect(() => {
    let cancelled = false;
    const params = {
      page, page_size: pageSize,
      q: search || undefined,
      sort_by: sort?.key, sort_dir: sort?.dir,
      ...filters,
    };
    fetcher(params)
      .then(({ data }) => { if (!cancelled) setResult({ key: requestKey, data, error: false }); })
      .catch(() => { if (!cancelled) setResult({ key: requestKey, data: null, error: true }); });
    return () => { cancelled = true; };
    // `filters` is captured through queryKey (serialised) on purpose
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  const loading = result.key !== requestKey;
  const data    = result.data;
  const rows    = data?.items ?? [];
  const total   = data?.total ?? 0;
  const pages   = data?.pages ?? 1;
  const from    = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to      = Math.min(page * pageSize, total);

  function toggleSort(key) {
    setSort((s) => (s?.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: "asc" }));
  }

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h3 className="font-semibold text-gray-700">
          {title} {data && <span className="text-gray-400 font-normal">({total.toLocaleString("es-PE")})</span>}
        </h3>
        <div className="flex flex-wrap items-center gap-2">
          {toolbar}
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder={searchPlaceholder}
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-64 focus:ring-2 focus:ring-blue-400 focus:outline-none"
          />
        </div>
      </div>

      <div className={`overflow-x-auto transition-opacity ${loading ? "opacity-50" : ""}`}>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b text-xs uppercase tracking-wide">
              {columns.map((c) => {
                const active = sort?.key === c.key;
                const Icon = !c.sortable ? null : active ? (sort.dir === "asc" ? ChevronUp : ChevronDown) : ChevronsUpDown;
                return (
                  <th key={c.key} className={`pb-2 pr-4 ${c.className ?? ""}`}>
                    {c.sortable ? (
                      <button onClick={() => toggleSort(c.key)}
                        className={`inline-flex items-center gap-1 uppercase tracking-wide ${active ? "text-gray-700" : "hover:text-gray-600"}`}>
                        {c.label} <Icon size={12} />
                      </button>
                    ) : c.label}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {result.error && (
              <tr><td colSpan={columns.length} className="py-6 text-center text-red-500">
                No se pudieron cargar los datos
              </td></tr>
            )}
            {!result.error && data && rows.length === 0 && (
              <tr><td colSpan={columns.length} className="py-6 text-center text-gray-400">{emptyMessage}</td></tr>
            )}
            {!data && !result.error && (
              <tr><td colSpan={columns.length} className="py-10 text-center text-gray-400">Cargando...</td></tr>
            )}
            {rows.map((row) => (
              <tr key={row[rowKey]} className="border-b border-gray-50 hover:bg-gray-50">
                {columns.map((c) => (
                  <td key={c.key} className={`py-2 pr-4 text-gray-600 ${c.className ?? ""}`}>
                    {c.render ? c.render(row) : (row[c.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 mt-4 text-sm text-gray-500">
        <div className="flex items-center gap-3">
          <span>Mostrando {from.toLocaleString("es-PE")}–{to.toLocaleString("es-PE")} de {total.toLocaleString("es-PE")}</span>
          <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}
            className="border border-gray-200 rounded-lg px-2 py-1 text-sm">
            {PAGE_SIZES.map((n) => <option key={n} value={n}>{n} por página</option>)}
          </select>
        </div>

        <div className="flex items-center gap-1">
          <button onClick={() => goTo(page - 1)} disabled={page <= 1}
            className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50" aria-label="Anterior">
            <ChevronLeft size={16} />
          </button>
          {pageWindow(page, pages).map((p) =>
            typeof p === "string" ? (
              <span key={p} className="px-1 text-gray-400">…</span>
            ) : (
              <button key={p} onClick={() => goTo(p)}
                className={`min-w-8 px-2 py-1 rounded-lg border text-sm ${
                  p === page ? "bg-blue-600 border-blue-600 text-white" : "border-gray-200 hover:bg-gray-50"}`}>
                {p}
              </button>
            )
          )}
          <button onClick={() => goTo(page + 1)} disabled={page >= pages}
            className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50" aria-label="Siguiente">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </Card>
  );
}
