// src/app/router/guards/RequireGuest.jsx

import { Navigate, Outlet } from "react-router-dom";
import { useSelector } from "react-redux";
import { DEFAULT_AFTER_LOGIN } from "../../../shared/lib/authRedirect";

export default function RequireGuest() {
  const accessToken = useSelector((s) => s.auth?.accessToken);
  const hydrated = useSelector((s) => s.auth?.hydrated);

  if (!hydrated) return null; // или <FullScreenLoader/>

  // Если пользователь авторизован — гостевые страницы ему не нужны
  if (accessToken) {
    return <Navigate to={DEFAULT_AFTER_LOGIN} replace />;
  }

  return <Outlet />;
}