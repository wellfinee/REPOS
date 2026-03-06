import React from "react";

export default function AchievementItem({ ua }) {
  const a = ua?.achievement ?? {};
  const iconUrl = a?.icon_file?.url || null;

  return (
    <div style={rowStyle}>
      <div style={{ width: 44, height: 44, borderRadius: 10, overflow: "hidden", border: "1px solid rgba(255,255,255,0.12)" }}>
        {iconUrl ? (
          <img src={iconUrl} alt={a.title || "achievement"} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div style={{ width: "100%", height: "100%", display: "grid", placeItems: "center", opacity: 0.6 }}>
            🏆
          </div>
        )}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, display: "flex", gap: 8, alignItems: "center" }}>
          <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{a.title || "—"}</span>
          {a.code ? <span style={codeStyle}>{a.code}</span> : null}
        </div>
        {a.description ? <div style={{ opacity: 0.75, fontSize: 12 }}>{a.description}</div> : null}

        <div style={{ marginTop: 6, fontSize: 12, opacity: 0.7 }}>
          Получено: {ua?.awarded_at ? new Date(ua.awarded_at).toLocaleString("ru-RU") : "—"}
        </div>
      </div>
    </div>
  );
}

const rowStyle = {
  display: "flex",
  gap: 12,
  alignItems: "center",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 12,
  padding: 10,
};

const codeStyle = {
  fontSize: 11,
  opacity: 0.8,
  border: "1px solid rgba(255,255,255,0.18)",
  borderRadius: 999,
  padding: "2px 8px",
};