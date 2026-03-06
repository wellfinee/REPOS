import React from "react";

export default function RolesBadges({ roles }) {
  const list = Array.isArray(roles) ? roles : [];

  return (
    <div style={cardStyle}  className="profile__role">
      {list.length === 0 ? (
        <div style={{ opacity: 0.75 }}>—</div>
      ) : (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {list.map((r) => (
            <span key={r}  className="profile__who"> 
              {r}
            </span>
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