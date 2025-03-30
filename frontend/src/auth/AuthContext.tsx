import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useRef,
} from "react";
import useSWR from "swr";

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  getAccessToken: () => Promise<string | null>;
  user: User | null;
  setIsAuthenticated: (value: boolean) => void;
  setAccessToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export interface User {
  _id: string;
  name: string | null;
  email: string | null;
  google_data: {
    sub: string | null;
    name: string | null;
    email: string | null;
    picture: string | null;
    email_verified: boolean | null;
    locale: string | null;
  } | null;
  google_token: string | null;
}

const fetcher = async (url: string, token: string) => {
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error("Failed to fetch user data");
  return response.json();
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const isInitialized = useRef(false);

  // Use SWR for user data fetching
  const { data: user, isLoading: isUserLoading } = useSWR(
    accessToken ? [`${import.meta.env.VITE_API_URL}/me`, accessToken] : null,
    ([url, token]) => fetcher(url, token),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

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
      setIsAuthenticated(true);
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
          setIsAuthenticated(true);
        } else {
          // Token is invalid, clear it
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setAccessToken(null);
          setIsAuthenticated(false);
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
    setIsAuthenticated(false);
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

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading: isLoading || isUserLoading,
        login,
        logout,
        user: user || null,
        getAccessToken,
        setIsAuthenticated,
        setAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
