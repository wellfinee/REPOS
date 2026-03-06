import { http } from "./http"; // твой axios instance с интерцепторами

export async function getMe() {
  const { data } = await http.get("/api/auth/me/");
  if (!data?.success) {
    const msg = data?.errors?.detail || "Failed to load /me";
    throw new Error(msg);
  }
  return data.user;
}