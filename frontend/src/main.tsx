import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { Login } from "./pages/Login";
import { LandingPage } from "./pages/LandingPage";
import { TokenCallback } from "./pages/TokenCallback";
import App from "./App";
import MyTree from "./pages/MyTree";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <AuthProvider>
        <App />
      </AuthProvider>
    ),
    children: [
      {
        path: "/",
        element: <LandingPage />,
      },
      {
        path: "login",
        element: <Login />,
      },
      {
        path: "token",
        element: <TokenCallback />,
      },
      {
        path: "dashboard",
        element: (
          <ProtectedRoute>
            <MyTree />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
