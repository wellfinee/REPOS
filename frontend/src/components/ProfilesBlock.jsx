import React from "react";

export default function ProfilesBlock({ profiles, currentEnrollment }) {
  const student = profiles?.student ?? null;
  const teacher = profiles?.teacher ?? null;
  const parent = profiles?.parent ?? null;

  return (
    <div style={cardStyle} className="profile__accounts">
      <div style={titleStyle} className="profile__title-acc">Профили</div>

      <div className="profile__social">
        <Row label="Ученик" value={student ? `code: ${student.student_code || "—"}` : "—"} />
        <Row label="Учитель" value={teacher ? `staff: ${teacher.staff_code || "—"}` : "—"} />
        <Row label="Родитель" value={parent ? `user_id: ${parent.user_id}` : "—"} />
      </div>

      <div style={{ height: 12 }} />

      <div style={titleStyle}>Текущий класс</div>
      {currentEnrollment ? (
        <div style={{ opacity: 0.9 }}>
          {currentEnrollment.grade} класс • {currentEnrollment.class_group_name} •{" "}
          {currentEnrollment.academic_year_name}
        </div>
      ) : (
        <div style={{ opacity: 0.75 }}>—</div>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
      <div style={{ opacity: 0.7 }}>{label}</div>
      <div style={{ fontWeight: 600 }}>{value}</div>
    </div>
  );
}

const cardStyle = {
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 12,
  padding: 12,
};
const titleStyle = { fontSize: 14, opacity: 0.8, marginBottom: 6 };