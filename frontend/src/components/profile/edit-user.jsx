// src/features/user-profile/components/EditUserModal.jsx
import React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import ClassSelect from "./ClassSelect";
import SearchUserSelect from "./search-user";
import { useUserProfile, usePatchUserAdmin, usePatchStudentAdmin } from "../../features/profile/hook";

const userSchema = z.object({
  email: z.string().email().nullable().optional(),
  phone: z.string().min(3).nullable().optional(),
  full_name: z.string().min(1),
  role: z.enum(["ADMIN", "DIRECTOR", "TEACHER", "STUDENT", "PARENT"]).nullable().optional(),
  is_active: z.boolean().optional(),

  // student-only
  birth_date: z.string().nullable().optional(),
  current_class_id: z.string().uuid().nullable().optional(),

  parent_user: z
    .object({ id: z.string(), full_name: z.string().optional(), email: z.string().optional() })
    .nullable()
    .optional(),
  teacher_user: z
    .object({ id: z.string(), full_name: z.string().optional(), email: z.string().optional() })
    .nullable()
    .optional(),

  // для отображения выбранного класса (не обяз)
  current_class: z.any().nullable().optional(),
});

export default function EditUserModal({ open, onClose, canEdit, user, profiles }) {
  const profileQuery = useUserProfile(user?.id);

  const patchUser = usePatchUserAdmin(user?.id);
  const patchStudent = usePatchStudentAdmin(user?.id);

  const student = profiles?.student ?? null;

  // ✅ школа берётся “старая/текущая” из user/profile
  const schoolId =
    user?.school?.id ??
    profileQuery.data?.school?.id ??
    profileQuery.data?.school_id ??
    null;

  const form = useForm({
    resolver: zodResolver(userSchema),
    mode: "onChange",
    defaultValues: {
      email: user?.email ?? null,
      phone: user?.phone ?? null,
      full_name: user?.full_name ?? "",
      role: user?.role ?? null,
      is_active: !!user?.is_active,

      birth_date: student?.birth_date ?? null,
      current_class_id: student?.current_class?.id ?? null,
      current_class: student?.current_class ?? null,

      parent_user: student?.parent?.user ?? null,
      teacher_user: student?.teacher?.user ?? null,
    },
  });

  React.useEffect(() => {
    if (!open) return;

    form.reset({
      email: user?.email ?? null,
      phone: user?.phone ?? null,
      full_name: user?.full_name ?? "",
      role: user?.role ?? null,
      is_active: !!user?.is_active,

      birth_date: student?.birth_date ?? null,
      current_class_id: student?.current_class?.id ?? null,
      current_class: student?.current_class ?? null,

      parent_user: student?.parent?.user ?? null,
      teacher_user: student?.teacher?.user ?? null,
    });
  }, [open, user, student]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!open) return null;

  const isBusy = patchUser.isPending || patchStudent.isPending;
  const isLoadingProfile = profileQuery.isLoading;

  const role = form.watch("role");
  const isStudent = role === "STUDENT";

  async function onSubmit(values) {
    if (!canEdit) return;

    // ✅ school не трогаем
    const userPayload = {
      email: values.email || null,
      phone: values.phone || null,
      full_name: values.full_name,
      role: values.role ?? null,
      is_active: !!values.is_active,
    };

    await patchUser.mutateAsync({ payload: userPayload });

if (isStudent) {
  if (!student?.id) {
    alert("У пользователя нет профиля студента. Создайте его сначала через Django Admin.");
    return;
  }

      const studentPayload = {
        birth_date: values.birth_date || null,
        current_class_id: values.current_class_id || null,
        parent_user_id: values.parent_user?.id ?? null,
        teacher_user_id: values.teacher_user?.id ?? null,
      };

      await patchStudent.mutateAsync({ studentId: student.id, payload: studentPayload });
    }

    onClose();
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.35)",
        display: "grid",
        placeItems: "center",
        padding: 16,
        zIndex: 9999,
      }}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div style={{ width: "min(760px, 100%)", background: "#fff", borderRadius: 24, padding: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 18, fontWeight: 800, flex: 1 }}>Настройка пользователя</div>
          <button type="button" onClick={onClose} disabled={isBusy}>
            ✕
          </button>
        </div>

        {!canEdit ? (
          <div style={{ marginTop: 12, padding: 12, borderRadius: 12, background: "#fff5f5" }}>
            Нет прав: редактирование доступно только SCHOOL_ADMIN.
          </div>
        ) : null}

        {isLoadingProfile ? (
          <div style={{ marginTop: 12, padding: 12, borderRadius: 12, background: "#f6f6f6" }}>
            Загружаю профиль...
          </div>
        ) : null}

        {!schoolId ? (
          <div style={{ marginTop: 12, padding: 12, borderRadius: 12, background: "#fffbe6" }}>
            У пользователя не определена школа — поиск учителей/родителей и выбор класса будут недоступны.
          </div>
        ) : null}

        <form onSubmit={form.handleSubmit(onSubmit)} style={{ marginTop: 16, display: "grid", gap: 16 }}>
          <div style={{ display: "grid", gap: 8 }}>
            <div style={{ fontWeight: 600 }}>ФИО</div>
            <input
              disabled={!canEdit || isBusy}
              {...form.register("full_name")}
              style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontWeight: 600 }}>Email</div>
              <input
                disabled={!canEdit || isBusy}
                placeholder="user@mail.com"
                {...form.register("email")}
                style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
              />
            </div>
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontWeight: 600 }}>Телефон</div>
              <input
                disabled={!canEdit || isBusy}
                placeholder="+998..."
                {...form.register("phone")}
                style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 12, alignItems: "end" }}>
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontWeight: 600 }}>Роль</div>
              <select
                disabled={!canEdit || isBusy}
                {...form.register("role")}
                style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
                onChange={(e) => {
                  const next = e.target.value;
                  form.setValue("role", next, { shouldDirty: true, shouldValidate: true });

                  if (next !== "STUDENT") {
                    form.setValue("birth_date", null, { shouldDirty: true });
                    form.setValue("current_class_id", null, { shouldDirty: true });
                    form.setValue("current_class", null, { shouldDirty: true });
                    form.setValue("parent_user", null, { shouldDirty: true });
                    form.setValue("teacher_user", null, { shouldDirty: true });
                  }
                }}
              >
                <option value="ADMIN">ADMIN</option>
                <option value="DIRECTOR">DIRECTOR</option>
                <option value="TEACHER">TEACHER</option>
                <option value="STUDENT">STUDENT</option>
                <option value="PARENT">PARENT</option>
              </select>
            </div>

            <label style={{ display: "flex", gap: 10, alignItems: "center", padding: "0 8px" }}>
              <input type="checkbox" disabled={!canEdit || isBusy} {...form.register("is_active")} />
              <span style={{ fontWeight: 600 }}>Активен</span>
            </label>
          </div>

          {isStudent ? (
            <div style={{ padding: 12, borderRadius: 16, border: "1px solid #eee", display: "grid", gap: 16 }}>
              <div style={{ fontWeight: 800 }}>Профиль ученика</div>

              <div style={{ display: "grid", gap: 8 }}>
                <div style={{ fontWeight: 600 }}>Дата рождения</div>
                <input
                  type="date"
                  disabled={!canEdit || isBusy}
                  {...form.register("birth_date")}
                  style={{ padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
                />
              </div>

              <ClassSelect
                label="Текущий класс"
                schoolId={schoolId}
                disabled={!canEdit || isBusy || !schoolId}
                value={form.watch("current_class") || null}
                onChange={(c) => {
                  form.setValue("current_class_id", c?.id ?? null, { shouldDirty: true, shouldValidate: true });
                  form.setValue("current_class", c ?? null, { shouldDirty: true });
                }}
              />

              <SearchUserSelect
                label="Родитель"
                role="PARENT"
                schoolId={schoolId}
                disabled={!canEdit || isBusy || !schoolId}
                value={form.watch("parent_user") || null}
                onChange={(u) =>
                  form.setValue("parent_user", u ? { ...u } : null, { shouldDirty: true, shouldValidate: true })
                }
              />

              <SearchUserSelect
                label="Учитель"
                role="TEACHER"
                schoolId={schoolId}
                disabled={!canEdit || isBusy || !schoolId}
                value={form.watch("teacher_user") || null}
                onChange={(u) =>
                  form.setValue("teacher_user", u ? { ...u } : null, { shouldDirty: true, shouldValidate: true })
                }
              />
            </div>
          ) : null}

          {(patchUser.isError || patchStudent.isError) ? (
            <div style={{ padding: 12, borderRadius: 12, background: "#fff5f5" }}>
              Ошибка сохранения. Проверь права/валидность/сервер.
            </div>
          ) : null}

          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button type="button" onClick={onClose} disabled={isBusy}>
              Отмена
            </button>
            <button type="submit" disabled={!canEdit || isBusy || !form.formState.isDirty}>
              {isBusy ? "Сохраняю..." : "Сохранить"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}