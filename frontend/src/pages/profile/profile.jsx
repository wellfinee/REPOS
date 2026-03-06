// src/features/user-profile/components/UserProfilePage.jsx
import React from "react";
import { useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { useUserProfile } from "./../../features/profile/hook";
import EditStudentModal from "./../../components/profile/edit-user";
import Button from "../../components/buttons/Button";
import "./profile.css"

export function useMyRoles() {
  const storeRoles = useSelector((s) => s.auth?.me?.roles ?? []);

  // 1) сразу читаем localStorage (чтобы не было "первый рендер пустой")
  const [roles, setRoles] = React.useState(() => {
    const cached = localStorage.getItem("my_roles");
    return cached ? cached.split(",").filter(Boolean) : [];
  });

  // 2) когда пришли роли из store — обновляем state и кэш
  React.useEffect(() => {
    if (Array.isArray(storeRoles) && storeRoles.length) {
      setRoles(storeRoles);
      localStorage.setItem("my_roles", storeRoles.join(","));
    }
  }, [storeRoles]);

  return roles;
}
export default function UserProfilePage() {
  const { id } = useParams();
  const { data, isLoading, isError } = useUserProfile(id);
  const myRoles = useMyRoles();
  const canEdit = myRoles.includes("SCHOOL_ADMIN");

  const [editOpen, setEditOpen] = React.useState(false);

  if (isLoading) return <div style={{ padding: 24 }}>Loading…</div>;
  if (isError || !data) return <div style={{ padding: 24 }}>Ошибка загрузки профиля</div>;

  const student = data?.profiles?.student;

  return (
    <div style={{ padding: 24, display: "grid", gap: 16 }}>
      {/* Header */}
      <div style={{ border: "2px solid #222", borderRadius: 24, padding: 16, display: "flex", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <div className="profile__name" style={{ fontSize: 20, fontWeight: 700 }}>{data.full_name}</div>
          <div style={{ fontWeight: 700 }}>{data.email}</div>
          <div style={{ opacity: 0.7, fontSize: 12 }}>User ID: {data.id}</div>
        </div>
        <div style={{ alignSelf: "start", padding: "8px 14px", border: "2px solid #222", borderRadius: 999 }}>
          {(data.roles?.[0] || "USER").toUpperCase()}
        </div>
      </div>

      {/* Cards row */}
      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 16, alignItems: "start" }}>
        {/* Wallet */}
        <div style={{ border: "2px solid #222", borderRadius: 24, padding: 16 }}>
          <div style={{ fontSize: 28, fontWeight: 800 }}>Кошелёк</div>
          <div style={{ marginTop: 12, fontSize: 28, fontWeight: 900 }}>
            {data.wallet?.balance ?? 0} 🪙
          </div>
        </div>

        {/* Profiles */}
        <div style={{ border: "2px solid #222", borderRadius: 24, padding: 16 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 800, flex: 1 }}>Профили</div>


          </div>

          <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
            <Row label="Ученик" value={student ? `Да (${student.student_code || "-"})` : "—"} />
            <Row
              label="Учитель"
              value={student?.teacher?.user ? student.teacher.user.full_name || student.teacher.user.email : "—"}
            />
            <Row
              label="Родитель"
              value={student?.parent?.user ? student.parent.user.full_name || student.parent.user.email : "—"}
            />
            <Row label="Текущий класс" value={student?.current_class?.title || "—"} />
          </div>
        </div>
      </div>

      {/* Achievements */}
      <div style={{ border: "2px solid #222", borderRadius: 24, padding: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 28, fontWeight: 800, flex: 1 }}>Достижения</div>
          <input
            placeholder="Поиск по достижениям…"
            style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd", width: 280 }}
          />
        </div>
        <div style={{ marginTop: 8, opacity: 0.7, fontSize: 12 }}>Показано: 0 / 0</div>
        <div style={{ marginTop: 8 }}>Пусто</div>
      </div>

      <EditStudentModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        user={data}
        profiles={data?.student}
        canEdit={canEdit}
      />
      {canEdit ? (
        <Button type="button" onClick={() => setEditOpen(true)} style={{ padding: "8px 12px" }} text="Настроить" />
      ) : null}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: 12 }}>
      <div style={{ opacity: 0.7 }}>{label}</div>
      <div style={{ textAlign: "right" }}>{value}</div>
    </div>
  );
}