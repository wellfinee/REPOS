import { Outlet, NavLink } from "react-router-dom";

export default function AppLayout() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", minHeight: "100vh" }}>
      <aside style={{ padding: 20, borderRight: "1px solid #eee" }}>
        <h2>Enterprise LMS</h2>
        <nav>
          <NavLink to="/">Dashboard</NavLink><br/>
          <NavLink to="/students">Students</NavLink>
        </nav>
      </aside>
      <main style={{ padding: 20 }}>
        <Outlet />
      </main>
    </div>
  );
}
