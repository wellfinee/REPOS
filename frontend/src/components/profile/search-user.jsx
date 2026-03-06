// src/features/user-profile/components/SearchUserSelect.jsx
import React from "react";
import { useUserSearch } from "./../../features/profile/hook";

function useDebouncedValue(value, delay = 300) {
  const [v, setV] = React.useState(value);
  React.useEffect(() => {
    const t = setTimeout(() => setV(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return v;
}

export default function SearchUserSelect({
  label,
  role,               // "PARENT" | "TEACHER"
  value,              // { id, full_name, email } | null
  onChange,
  disabled,
}) {
  const [q, setQ] = React.useState("");
  const debounced = useDebouncedValue(q, 300);

  const search = useUserSearch();
  const [items, setItems] = React.useState([]);

  React.useEffect(() => {
    let cancelled = false;

    async function run() {
      if (!debounced || debounced.trim().length < 2) {
        setItems([]);
        return;
      }
      try {
        const data = await search.mutateAsync({ role, q: debounced, limit: 20, offset: 0 });
        if (!cancelled) setItems(data.results || []);
      } catch {
        if (!cancelled) setItems([]);
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [debounced, role]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div style={{ fontWeight: 600 }}>{label}</div>

      <input
        disabled={disabled}
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={`Поиск ${role.toLowerCase()}... (мин. 2 символа)`}
        style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
      />

      {value ? (
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ flex: 1, padding: 10, borderRadius: 12, border: "1px solid #eee" }}>
            <div style={{ fontWeight: 600 }}>{value.full_name || "Без имени"}</div>
            <div style={{ opacity: 0.7, fontSize: 12 }}>{value.email}</div>
          </div>
          <button type="button" disabled={disabled} onClick={() => onChange(null)}>
            Очистить
          </button>
        </div>
      ) : null}

      {items.length > 0 ? (
        <div style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
          {items.map((u) => (
            <button
              key={u.id}
              type="button"
              disabled={disabled}
              onClick={() => onChange(u)}
              style={{
                width: "100%",
                textAlign: "left",
                padding: 10,
                border: "none",
                borderBottom: "1px solid #f2f2f2",
                background: "white",
                cursor: "pointer",
              }}
            >
              <div style={{ fontWeight: 600 }}>{u.full_name || "Без имени"}</div>
              <div style={{ opacity: 0.7, fontSize: 12 }}>{u.email}</div>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}