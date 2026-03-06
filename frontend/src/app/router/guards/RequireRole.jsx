import { Navigate, Outlet } from "react-router-dom";
import { useSelector } from "react-redux";

export default function RequireRole({ allow }) {
  const roles = useSelector((s) => s.auth?.me?.roles ?? []);
  const hasRole = Array.isArray(roles) && roles.some((r) => allow.includes(r));

  if (!hasRole) {
    return <Navigate to="/403" replace />;
  }

  return <Outlet />;
}
