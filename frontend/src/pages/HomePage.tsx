import { useAuth0 } from "@auth0/auth0-react";

export const HomePage = () => {
  const { user, logout } = useAuth0();

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Welcome, {user?.name}</h1>
        <button
          onClick={() =>
            logout({ logoutParams: { returnTo: window.location.origin } })
          }
          className="btn btn-outline"
        >
          Log Out
        </button>
      </div>
      {/* Add your protected content here */}
    </div>
  );
};
