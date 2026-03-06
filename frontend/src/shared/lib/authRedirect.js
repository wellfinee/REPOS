// src/shared/lib/authRedirect.js

export const DEFAULT_AFTER_LOGIN = "/";

/**
 * Нормализуем from:
 * - поддерживает строку "/path" и объект { pathname, search }
 */
export function normalizeFrom(from) {
  if (!from) return null;

  if (typeof from === "string") return from;

  if (typeof from === "object" && typeof from.pathname === "string") {
    const search = typeof from.search === "string" ? from.search : "";
    return `${from.pathname}${search}`;
  }

  return null;
}

/**
 * Защита от "плохого" редиректа:
 * - только внутренние пути начинающиеся с "/"
 * - не редиректим на auth-страницы
 */
export function getSafeRedirect(from, options = {}) {
  const {
    fallback = DEFAULT_AFTER_LOGIN,
    blockedPrefixes = ["/login", "/register", "/forgot-password", "/auth"],
  } = options;

  const raw = normalizeFrom(from);
  if (!raw) return fallback;

  // Только внутренние пути
  if (!raw.startsWith("/")) return fallback;

  // Блокируем auth-страницы (и любые их подпути)
  if (blockedPrefixes.some((p) => raw === p || raw.startsWith(`${p}/`) || raw.startsWith(p))) {
    return fallback;
  }

  return raw;
}