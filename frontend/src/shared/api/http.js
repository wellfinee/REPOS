// src/shared/api/http.js
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// ---- injected handlers (set via initHttpAuth) ----
let getAccessToken = () => null;
let onNewAccessToken = (_token) => { };
let onHardLogout = () => { };

export function initHttpAuth(handlers) {
    if (!handlers || typeof handlers.getAccessToken !== "function") {
    throw new Error("initHttpAuth: handlers.getAccessToken must be a function");
  }
  getAccessToken = handlers.getAccessToken || (() => null);
  onNewAccessToken = handlers.onNewAccessToken || (() => { });
  onHardLogout = handlers.onHardLogout || (() => { });
}

// ---- helpers ----
// ---- helpers ----
const attachBearer = (config, token) => {
  if (!token) return config;

  // Axios v1 headers: AxiosHeaders (has set/get)
  if (config.headers && typeof config.headers.set === "function") {
    config.headers.set("Authorization", `Bearer ${token}`);
    return config;
  }

  config.headers = config.headers || {};
  config.headers.Authorization = `Bearer ${token}`;
  return config;
};

const hasAuthHeader = (config) => {
  const h = config?.headers;
  if (!h) return false;

  if (typeof h.get === "function") {
    return Boolean(h.get("Authorization") || h.get("authorization"));
  }

  return Boolean(h.Authorization || h.authorization);
};
const getPathname = (config) => {
  const url = config?.url || "";
  if (/^https?:\/\//i.test(url)) {
    try { return new URL(url).pathname; } catch { return url; }
  }
  return url.startsWith("/") ? url : `/${url}`;
};

const isAuthEndpoint = (config) => {
  const p = getPathname(config);
  return (
    p === "/api/auth/login/" ||
    p === "/api/auth/refresh/" ||
    p === "/api/auth/logout/"
  );
};

let isRefreshing = false;
let queue = [];

const resolveQueue = (token) => { queue.forEach(p => p.resolve(token)); queue = []; };
const rejectQueue = (err) => { queue.forEach(p => p.reject(err)); queue = []; };

async function refreshAccessToken() {
  console.log("[refresh] calling /api/auth/refresh/");
  const { data } = await refreshClient.post("/api/auth/refresh/", {});
  console.log("[refresh] response", data);
  const newAccess = data?.access ?? null;
  if (!newAccess) throw new Error("Refresh succeeded but no access in response");
  return newAccess;
}

// ---- request interceptor ----
http.interceptors.request.use((config) => {
  const p = getPathname(config);
  const skip = p === "/api/auth/login/" || p === "/api/auth/refresh/" || p === "/api/auth/logout/";
  if (!skip) {
    const token = getAccessToken();
    if (token) attachBearer(config, token);
  }
  return config;
});
// ---- response interceptor ----
http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error?.config;
    const resp = error?.response;

    // Network/CORS
    if (!original || !resp) return Promise.reject(error);

    // DEBUG: только для 403
    if (resp.status === 403) {
      console.log("[403] caught", {
        url: original?.url,
        baseURL: original?.baseURL,
        tokenInStore: Boolean(getAccessToken()),
        withCredentials: original?.withCredentials,
        headersHasGet: Boolean(original?.headers && typeof original.headers.get === "function"),
        authHeaderViaGet:
          original?.headers && typeof original.headers.get === "function"
            ? original.headers.get("Authorization")
            : undefined,
        authHeaderRaw:
          original?.headers?.Authorization || original?.headers?.authorization,
      });
    }

    // refresh только на 403
    if (resp.status !== 403) return Promise.reject(error);

    // не refresh’им auth endpoints
    if (isAuthEndpoint(original)) return Promise.reject(error);

    // если токена нет в store — refresh невозможен
    const tokenInStore = getAccessToken();
    if (!tokenInStore) return Promise.reject(error);

    // защита от бесконечного ретрая
    if (original._retry) {
      onHardLogout();
      return Promise.reject(error);
    }
    original._retry = true;

    // очередь во время refresh
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push({
          resolve: (token) => resolve(http(attachBearer(original, token))),
          reject,
        });
      });
    }

    isRefreshing = true;

    try {
      const newAccess = await refreshAccessToken(); // тут должен быть лог "[refresh] calling"
      onNewAccessToken(newAccess);
      resolveQueue(newAccess);
      return http(attachBearer(original, newAccess));
    } catch (refreshErr) {
      rejectQueue(refreshErr);
      onHardLogout();
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);