import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { loginRequest, logoutRequest, meRequest } from "../response/auth";

const TOKEN_KEY = "accessToken";
const REMEMBER_KEY = "auth_rememberMe";

/** ---------- Storage helpers ---------- */
function writeRememberMe(value) {
  localStorage.setItem(REMEMBER_KEY, value ? "1" : "0");
}

function readRememberMe() {
  const v = localStorage.getItem(REMEMBER_KEY);
  if (v === "1") return true;
  if (v === "0") return false;
  return null; // неизвестно (первый запуск)
}

function writeToken(token, rememberMe) {
  // чистим оба, чтобы не было конфликтов
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);

  if (!token) return;

  if (rememberMe) localStorage.setItem(TOKEN_KEY, token);
  else sessionStorage.setItem(TOKEN_KEY, token);
}

function readToken() {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
}

function extractError(err, fallback = "Request failed") {
  // твой бэк часто отдаёт: { success:false, errors:{detail:"..."} }
  return (
    err?.response?.data?.errors?.detail ||
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}

/** ---------- Thunks ---------- */
export const login = createAsyncThunk(
  "auth/login",
  async ({ email, password, rememberMe }, { rejectWithValue, dispatch }) => {
    try {
      const res = await loginRequest(email, password, rememberMe);

      const access = res?.accessToken ?? res?.access ?? res?.token ?? null;
      if (!access) return rejectWithValue("Access token missing in login response.");

      // политика persist
      writeRememberMe(Boolean(rememberMe));

      // ✅ 1) Сразу кладём токен в store (+ storage через reducer)
      dispatch(setAccessToken({ token: access, rememberMe: Boolean(rememberMe) }));

      // ✅ 2) Потом /me (уже с Authorization)
      const me = await meRequest(); // после фикса meRequest вернёт user

      if (!me) return rejectWithValue("Failed to load /me after login.");

      return {
        accessToken: access,
        me,
        rememberMe: Boolean(rememberMe),
        raw: res,
      };
    } catch (err) {
      return rejectWithValue(extractError(err, "Login failed"));
    }
  }
);
export const fetchMe = createAsyncThunk(
  "auth/fetchMe",
  async (_, { rejectWithValue }) => {
    try {
      // axios interceptor сам сделает refresh если access expired
      const data = await meRequest();

      // поддержка форматов:
      // { success:true, user:{...} } или просто user
      const user = data?.user ?? data;
      return user;
    } catch (err) {
      return rejectWithValue(extractError(err, "Failed to load profile"));
    }
  }
);

export const logout = createAsyncThunk("auth/logout", async (_, { dispatch }) => {
  try {
    await logoutRequest();
  } catch (_) {
    // даже если бэк умер — мы всё равно чистим локально
  } finally {
    dispatch(authSlice.actions.hardLogout());
  }
  return true;
});

/** ---------- Slice ---------- */

const initialState = {
  accessToken: null,
  me: null,

  // rememberMe — это политика сохранения access token
  // null = не определено (до hydrate/login)
  rememberMe: null,

  loginStatus: "idle", // idle | loading | succeeded | failed
  meStatus: "idle",    // idle | loading | succeeded | failed
  error: null,

  hydrated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    /**
     * Вызывай один раз при старте приложения (до роутера).
     * Поднимает accessToken и rememberMe.
     */
    hydrateAuth(state) {
      state.accessToken = readToken();
      state.rememberMe = readRememberMe();
      state.hydrated = true;
    },

    /**
     * Используется axios interceptor'ом после refresh:
     * store.dispatch(setAccessToken(newAccess))
     *
     * ИЛИ можно передать объект:
     * setAccessToken({ token, rememberMe })
     */
    setAccessToken(state, action) {
      const payload = action.payload;

      const token =
        typeof payload === "string"
          ? payload
          : (payload?.token ?? null);

      const rememberMe =
        typeof payload === "object" && payload?.rememberMe !== undefined
          ? Boolean(payload.rememberMe)
          : state.rememberMe; // если не передали — используем сохранённую политику

      state.accessToken = token;

      // если политика неизвестна, но токен пришёл — по умолчанию НЕ сохраняем в localStorage,
      // а держим в sessionStorage (безопаснее)
      const effectiveRemember = rememberMe ?? false;

      // синхронизируем политику, если пришла
      if (typeof payload === "object" && payload?.rememberMe !== undefined) {
        state.rememberMe = Boolean(payload.rememberMe);
        writeRememberMe(Boolean(payload.rememberMe));
      }

      if (token) writeToken(token, effectiveRemember);
      else clearToken();
    },

    /**
     * Локальный logout без запроса (удобно для интерцептора/ошибок refresh).
     * Если refresh умер — делай store.dispatch(hardLogout()).
     */
    hardLogout(state) {
      state.accessToken = null;
      state.me = null;
      state.loginStatus = "idle";
      state.meStatus = "idle";
      state.error = null;
      // политику rememberMe можно оставить или сбросить — я оставлю, чтобы UX был стабильнее
      // state.rememberMe = null;
      clearToken();
    },

    clearAuthError(state) {
      state.error = null;
    },

    setUser(state, action) {
      state.me = action.payload ?? null;
    },
  },

  extraReducers: (builder) => {
    builder
      // login
      .addCase(login.pending, (state) => {
        state.loginStatus = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loginStatus = "succeeded";
        state.accessToken = action.payload.accessToken;
        state.me = action.payload.me;
        state.rememberMe = action.payload.rememberMe;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.loginStatus = "failed";
        state.error = action.payload || "Login failed";
      })

      // me
      .addCase(fetchMe.pending, (state) => {
        state.meStatus = "loading";
        state.error = null;
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.meStatus = "succeeded";
        state.me = action.payload;
      })
      .addCase(fetchMe.rejected, (state, action) => {
        state.meStatus = "failed";
        state.error = action.payload || "Failed to load profile";
      })

      // logout thunk always ends with hardLogout already
      .addCase(logout.fulfilled, (state) => state);
  },
});

export const { hydrateAuth, setAccessToken, hardLogout, clearAuthError, setUser } =
  authSlice.actions;

export default authSlice.reducer;

/** ---------- Selectors ---------- */
export const selectAccessToken = (s) => s.auth.accessToken;
export const selectUser = (s) => s.auth.me;
export const selectMe = (s) => s.auth.me;
export const selectLoginStatus = (s) => s.auth.loginStatus;
export const selectMeStatus = (s) => s.auth.meStatus;
export const selectAuthError = (s) => s.auth.error;
export const selectIsAuthenticated = (s) => Boolean(s.auth.accessToken);
export const selectAuthHydrated = (s) => s.auth.hydrated;
export const selectRememberMe = (s) => s.auth.rememberMe;