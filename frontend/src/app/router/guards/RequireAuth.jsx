// src/app/router/guards/RequireAuth.jsx

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";

export default function RequireAuth() {
  const location = useLocation();
  const accessToken = useSelector((s) => s.auth?.accessToken);
  const hydrated = useSelector((s) => s.auth?.hydrated);

  // Важно: пока auth не гидрирован — не редиректим (иначе будет "мигание" на /login)
  if (!hydrated) return null; // или <FullScreenLoader/>

  if (!accessToken) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: {
            pathname: location.pathname,
            search: location.search,
          },
        }}
      />
    );
  }

  return <Outlet />;
}