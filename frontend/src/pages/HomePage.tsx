import { useAuth } from "../auth/AuthContext";

export const HomePage = () => {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

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
