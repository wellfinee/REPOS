import React from "react";
import RolesBadges from "../RolesBadges";

export default function UserHeader({ user }) {
  const school = user.school?.name ? ` • ${user.school.name}` : "";

  return (
    <div style={cardStyle} className="profile__header">
      <div className="profile__container">
        <div className="profile__name" style={{ fontSize: 20, fontWeight: 700 }}>{user.full_name}</div>
        <div style={{ opacity: 0.8 }}>
          {user.email || "—"} {user.phone ? ` • ${user.phone}` : ""} {school}
        </div>
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>User ID: {user.id}</div>
      </div>
      <RolesBadges roles={user.roles} />
    </div>
  );
}

const cardStyle = {
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 12,
  padding: 12,
};