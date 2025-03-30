import { Outlet } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";

function App() {
  const { getAccessToken } = useAuth();

  const handleClick = async () => {
    try {
      const token = await getAccessToken();
      if (token) {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/api/protected`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await response.json();
        console.log(data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-grow">
        <Outlet />
      </main>
      <button className="btn btn-primary" onClick={handleClick}>
        Click me
      </button>
    </div>
  );
}

export default App;
