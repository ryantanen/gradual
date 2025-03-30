import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import useSWR from "swr";
import { useAuth } from "../auth/AuthContext";

export const TokenCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setIsAuthenticated, setAccessToken } = useAuth();

  // Get the authorization code from the URL
  const params = new URLSearchParams(location.search);
  const code = params.get("code");

  // Create a fetcher function for the token exchange
  const tokenFetcher = async (url: string) => {
    const response = await fetch(url, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        JSON.stringify({
          status: response.status,
          statusText: response.statusText,
          error: errorData,
        })
      );
    }

    return response.json();
  };

  // Use SWR to handle the token exchange
  const { data, error } = useSWR(
    code ? `${import.meta.env.VITE_API_URL}/auth/google?code=${code}` : null,
    tokenFetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 10000, // Prevent duplicate requests for 10 seconds
      shouldRetryOnError: false,
    }
  );

  // Create a separate SWR hook for token validation
  const validateToken = async (url: string) => {
    if (!data?.access_token) return null;

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${data.access_token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Token validation failed");
    }

    return true;
  };

  const { data: isValid, error: validationError } = useSWR(
    data?.access_token ? `${import.meta.env.VITE_API_URL}/token` : null,
    validateToken,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 10000,
      shouldRetryOnError: false,
    }
  );

  // Handle navigation based on SWR states
  useEffect(() => {
    // No code in URL
    if (!code) {
      navigate("/login");
      return;
    }

    // Error in token exchange
    if (error) {
      console.error("Failed to authenticate:", error);
      navigate("/login");
      return;
    }

    // Data received successfully
    if (data && !error) {
      // Store user info and token
      localStorage.setItem("user_info", JSON.stringify(data));

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        setAccessToken(data.access_token);
        setIsAuthenticated(true);

        // If token validation completed
        if (isValid === true) {
          console.log("Token is valid, navigating to home");
          navigate("/");
        } else if (validationError) {
          console.error("Token validation failed:", validationError);
          navigate("/login");
        }
      } else {
        console.error("No access token received from server");
        navigate("/login");
      }
    }
  }, [
    code,
    data,
    error,
    isValid,
    validationError,
    navigate,
    setIsAuthenticated,
    setAccessToken,
  ]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-semibold mb-4">Completing login...</h2>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    </div>
  );
};

export default TokenCallback;
