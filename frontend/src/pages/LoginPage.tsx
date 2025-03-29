import { useAuth0 } from "@auth0/auth0-react";

export const LoginPage = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome to Gradual</h1>
        <button onClick={() => loginWithRedirect()} className="btn btn-primary">
          Log In
        </button>
      </div>
    </div>
  );
};
