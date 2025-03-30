import { useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";

export const TokenCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isProcessing = useRef(false);

  const checkTokenValidity = async (token: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/token`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error("Token validation failed");
      }
      return true;
    } catch (error) {
      console.error("Error checking token validity:", error);
      return false;
    }
  };

  useEffect(() => {
    const handleCallback = async () => {
      if (isProcessing.current) return;
      isProcessing.current = true;

      try {
        // Get the authorization code from the URL
        const params = new URLSearchParams(location.search);
        const code = params.get("code");

        if (!code) {
          throw new Error("No authorization code received");
        }

        // Exchange the code for user info and token
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/google?code=${code}`,
          {
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error("Failed to authenticate with Google:", {
            status: response.status,
            statusText: response.statusText,
            error: errorData,
          });
          navigate("/login");
          return;
        }

        const data = await response.json();
        console.log("Auth response:", data);

        if (data.error || data.user.error) {
          console.error("Error in response:", data.error);
          navigate("/login");
          return;
        }

        // Store the user info
        localStorage.setItem("user_info", JSON.stringify(data));

        // Store the access token and validate it
        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token);
          const isValid = await checkTokenValidity(data.access_token);
          console.log("Token is valid:", isValid);
          if (isValid) {
            navigate("/");
          } else {
            throw new Error("Token validation failed");
          }
        } else {
          throw new Error("No access token received from server");
        }
      } catch (error) {
        console.error("Error during token callback:", error);
      } finally {
        isProcessing.current = false;
      }
    };

    handleCallback();

    return () => {
      isProcessing.current = false;
    };
  }, [navigate, location.search]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-semibold mb-4">Completing login...</h2>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    </div>
  );
};
