// src/features/user-profile/components/ClassSelect.jsx
import React from "react";
import { useClassSearch } from "./../../features/profile/hook";

function normalizeListResponse(data) {
  // поддержка форматов: [] | {results: []} | {items: []} | {data: []}
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

export default function ClassSelect({ label, schoolId, disabled, value, onChange }) {
  const search = useClassSearch();
  const [q, setQ] = React.useState("");
  const [options, setOptions] = React.useState([]);
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    if (!open) return;
    if (!schoolId) {
      setOptions([]);
      return;
    }

    const t = setTimeout(async () => {
      const res = await search.mutateAsync({ school_id: schoolId, q });
      setOptions(normalizeListResponse(res));
    }, 250);

    return () => clearTimeout(t);
  }, [q, open, schoolId]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div style={{ fontWeight: 600 }}>{label}</div>

      <input
        disabled={disabled || !schoolId}
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={schoolId ? "Поиск класса..." : "Сначала выбери школу"}
        style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
      />

      {open && !disabled ? (
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 8, maxHeight: 240, overflow: "auto" }}>
          {search.isPending ? (
            <div style={{ padding: 8, opacity: 0.7 }}>Ищу...</div>
          ) : options.length ? (
            options.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => {
                  onChange(c);
                  setOpen(false);
                  setQ("");
                }}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: 10,
                  borderRadius: 10,
                  border: "none",
                  background: value?.id === c.id ? "#f2f2f2" : "transparent",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontWeight: 700 }}>{c.name ?? c.title ?? c.grade_name ?? "Класс"}</div>
                <div style={{ fontSize: 12, opacity: 0.65 }}>{c.id}</div>
              </button>
            ))
          ) : (
            <div style={{ padding: 8, opacity: 0.7 }}>Ничего не найдено</div>
          )}
        </div>
      ) : null}

      {value ? (
        <div style={{ fontSize: 12, opacity: 0.7 }}>
          Выбрано: <b>{value.name ?? value.title ?? value.grade_name ?? value.id}</b>
        </div>
      ) : null}
    </div>
  );
}