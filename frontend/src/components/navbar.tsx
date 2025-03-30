import { useAuth } from "@/auth/AuthContext";
import { useState } from "react";

const Navbar = () => {
  const { user, isLoading, logout, getAccessToken } = useAuth();
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchAIData = async () => {
    const token = await getAccessToken();
    const response = await fetch(`${import.meta.env.VITE_API_URL}/begin-ai`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("Failed to fetch AI data");
    return response.json();
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await fetchAIData();
      // Start the 10 second delay after getting response
      await new Promise((resolve) => setTimeout(resolve, 15000));
      window.location.reload(); // Refresh the page after sync
    } catch (error) {
      console.error("Sync failed:", error);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="navbar bg-accent-content shadow-sm text-base-200">
      <div className="flex-1">
        <a className="btn btn-ghost text-3xl" href="/">
          Gradual.
        </a>
      </div>
      <button
        className="btn mx-5 text-black disabled:text-base-200"
        onClick={handleSync}
        disabled={isSyncing}
      >
        {isSyncing ? (
          <>
            <span className="loading loading-spinner"></span>
            Syncing...
          </>
        ) : (
          "Sync Data"
        )}
      </button>
      <div className="flex-none">
        <div className="dropdown dropdown-end">
          <div
            tabIndex={0}
            role="button"
            className="btn btn-ghost btn-circle avatar"
          >
            <div className="w-10 rounded-full">
              {isLoading && !user ? (
                <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
              ) : (
                <img
                  alt="User avatar"
                  src={user?.google_data?.picture || ""}
                  className="w-10 h-10 rounded-full object-cover"
                />
              )}
            </div>
          </div>
          <ul
            tabIndex={1}
            className="menu menu-sm dropdown-content rounded-box z-1 mt-4 w-52 p-2 shadow bg-slate-800 py-4"
          >
            <li>
              <a className="justify-between">
                Profile
                <span className="badge">New</span>
              </a>
            </li>
            <li>
              <a>Settings</a>
            </li>
            <li>
              <a onClick={() => logout()}>Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
