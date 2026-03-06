import React, { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";

import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import RequireAuth from "./guards/RequireAuth";
import RequireRole from "./guards/RequireRole";
import { ROLES } from "./../../shared/lib/roles";

const LoginPage = lazy(() => import("./../../pages/auth/LoginPage"));
const DashboardPage = lazy(() => import("./../../pages/dashboard/DashboardPage"));
const StudentsPage = lazy(() => import("./../../pages/students/StudentsPage"));
const StudentDetailsPage = lazy(() => import("./../../pages/students/StudentDetailsPage"));
const ForbiddenPage = lazy(() => import("./../../pages/system/ForbiddenPage"));
const NotFoundPage = lazy(() => import("./../../pages/system/NotFoundPage"));
const MePage = lazy(() => import("./../../pages/me/mePage"));
const UserProfilePage = lazy(() => import("./../../pages/profile/profile"));


function Lazy({ children }) {
  return <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: "/login", element: <Lazy><LoginPage /></Lazy> },
      { path: "/403", element: <Lazy><ForbiddenPage /></Lazy> },
    ],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <Lazy><DashboardPage /></Lazy> },
          { path: "/me", element: <Lazy><MePage /></Lazy> },
          { path: "/users/:id", element: <Lazy><UserProfilePage /></Lazy> },  
          {
            element: <RequireRole allow={[ROLES.ADMIN, ROLES.DIRECTOR, ROLES.TEACHER]} />,
            children: [
              { path: "/students", element: <Lazy><StudentsPage /></Lazy> },
              { path: "/students/:id", element: <Lazy><StudentDetailsPage /></Lazy> },
            ],
          },
          { path: "*", element: <Lazy><NotFoundPage /></Lazy> },
        ],
      },
    ],
  },
]);
