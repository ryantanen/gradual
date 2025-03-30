import { useAuth } from "@/auth/AuthContext";

const Navbar = () => {
  const { user, isLoading, logout } = useAuth();

  return (
    <div className="navbar bg-accent-content shadow-sm text-base-200">
      <div className="flex-1">
        <a className="btn btn-ghost text-3xl">Gradual.</a>
      </div>
      <button className="btn mx-5">Share Timeline</button>
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
