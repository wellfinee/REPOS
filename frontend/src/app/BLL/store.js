// src/app/BLL/store.js
import { configureStore } from "@reduxjs/toolkit";
import authReducer, { setAccessToken, hardLogout } from "./authReducer";
import { initHttpAuth } from "../../shared/api/http";
import myReducer from "./myReducer"

export const store = configureStore({
  reducer: {
    auth: authReducer,
    me: myReducer
  },
});

// ✅ после создания store подключаем http к redux
initHttpAuth({
  getAccessToken: () => store.getState()?.auth?.accessToken ?? null,
  onNewAccessToken: (token) => store.dispatch(setAccessToken(token)),
  onHardLogout: () => store.dispatch(hardLogout()),
});
