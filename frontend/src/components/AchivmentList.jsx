import React, { useMemo, useState } from "react";
import AchievementItem from "./AchivmentItem";

export default function AchievementsList({ achievements }) {
  const [q, setQ] = useState("");
  const list = Array.isArray(achievements) ? achievements : [];

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return list;
    return list.filter((ua) => {
      const a = ua?.achievement;
      const hay = `${a?.code || ""} ${a?.title || ""} ${a?.description || ""}`.toLowerCase();
      return hay.includes(query);
    });
  }, [list, q]);

  return (
    <div style={cardStyle} className="profile__achivement">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div style={titleStyle} className="profile__title-acc">  Достижения</div>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Поиск по достижениям…"
          style={inputStyle}
        />
      </div>

      <div style={{ opacity: 0.75, fontSize: 12, marginBottom: 10 }}>
        Показано: {filtered.length} / {list.length}
      </div>

      {filtered.length === 0 ? (
        <div style={{ opacity: 0.75 }}>Пусто</div>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {filtered.map((ua, idx) => (
            <AchievementItem key={`${ua?.achievement?.id || "x"}-${idx}`} ua={ua} />
          ))}
        </div>
      )}
    </div>
  );
}

const cardStyle = {
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 12,
  padding: 12,
};
const titleStyle = { fontSize: 14, opacity: 0.8 };
const inputStyle = {
  padding: "8px 10px",
  borderRadius: 10,
  border: "1px solid rgba(255,255,255,0.18)",
  background: "transparent",
  color: "inherit",
  outline: "none",
  width: 260,
};