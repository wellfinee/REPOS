import React from "react";

export default function WalletCard({ wallet }) {
  const balance = Number(wallet?.balance ?? 0);

  return (
    <div style={cardStyle} className="profile__wallet">
      <div style={titleStyle} className="profile__title-acc">Кошелёк</div>
      <div style={{ fontSize: 28, fontWeight: 800, display:"flex", gap: "10px" }}>{balance.toLocaleString("ru-RU")} <span>🪙</span></div>
    </div>
  );
}

const cardStyle = {
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 12,
  padding: 12,
};
const titleStyle = { fontSize: 14, opacity: 0.8, marginBottom: 6 };