// src/shared/api/classes.js
import {http} from "./http"

// ожидаем endpoint типа /api/admin/classes/?school_id=...&q=...
export async function listClasses({ school_id, q }) {
  const { data } = await http.get("/api/admin/classes/", {
    params: {
      school_id,
      q: q || undefined,
      limit: 20,
    },
  });
  return data;
}