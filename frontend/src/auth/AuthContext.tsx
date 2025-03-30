import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useRef,
} from "react";

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  getAccessToken: () => Promise<string | null>;
  getUser: () => Promise<{ sub: string; name: string; picture: string }>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const isInitialized = useRef(false);

  // Function to refresh the access token
  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) return null;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error("Failed to refresh token");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      setAccessToken(data.access_token);
      return data.access_token;
    } catch (error) {
      console.error("Error refreshing token:", error);
      logout();
      return null;
    }
  };

  // Function to check if token is valid
  const checkTokenValidity = async (token: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/token`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        // Try to refresh the token if validation fails
        const newToken = await refreshAccessToken();
        if (newToken) {
          return true;
        }
        throw new Error("Token validation failed");
      }
      return true;
    } catch (error) {
      console.error("Error checking token validity:", error);
      return false;
    }
  };

  // Function to initialize auth state
  const initializeAuth = async () => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    try {
      const token = localStorage.getItem("access_token");
      if (token) {
        const isValid = await checkTokenValidity(token);
        if (isValid) {
          setAccessToken(token);
        } else {
          // Token is invalid, clear it
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setAccessToken(null);
        }
      }
    } catch (error) {
      console.error("Error initializing auth:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isInitialized.current) {
      initializeAuth();
    }
    return () => {
      isInitialized.current = false;
    };
  }, []);

  const login = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/login/google`;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_info");
    setAccessToken(null);
  };

  const getAccessToken = async () => {
    if (accessToken) {
      const isValid = await checkTokenValidity(accessToken);
      if (isValid) {
        return accessToken;
      }
    }

    // If we get here, authentication failed
    logout();
    return null;
  };

  // Compute isAuthenticated based on localStorage
  const isAuthenticated = !!localStorage.getItem("access_token");

  const getUser = async () => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/me`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });
    return response.json();
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        login,
        logout,
        getUser,
        getAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
