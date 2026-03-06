import { http } from "../../shared/api/http";

export async function loginRequest(email, password, rememberMe) {
  const { data } = await http.post("/api/auth/login/", {
    identifier: email,
    password,
    remember_me: rememberMe,
  });

  const accessToken = data?.accessToken ?? data?.access ?? data?.token ?? null;
  const user = data?.user ?? null;

  return { accessToken, user, raw: data };
}

export async function logoutRequest() {
  await http.post("/api/auth/logout/", {});
  return true;
}

export async function meRequest() {
  const { data } = await http.get("/api/auth/me/");
  // твой бек: { success:true, user:{...} }
  return data?.user ?? null;
}