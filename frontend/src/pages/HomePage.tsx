import { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";

export const HomePage = () => {
  const { logout, getUser } = useAuth();
  const [user, setUser] = useState<{
    sub: string;
    name: string;
    picture: string;
  } | null>(null);
  useEffect(() => {
    const fetchUser = async () => {
      const user = await getUser();
      setUser(user);
    };
    fetchUser();
  }, []);
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-base-200 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Welcome to your Dashboard</h2>
        <p className="text-base-content/70">
          This is your protected home page. Add your content here.
          {JSON.stringify(user)}
          <button onClick={logout} className="btn btn-error">
            Logout
          </button>
        </p>
      </div>
    </div>
  );
};
