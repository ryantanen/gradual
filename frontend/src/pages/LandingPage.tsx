import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export const LandingPage = () => {
  const { user, isLoading } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="hero min-h-screen bg-base-200">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">Welcome to Gradual</h1>
            <p className="py-6">
              Your personal journey of growth and development starts here. Track
              your progress, set goals, and watch yourself evolve.
            </p>
            {isLoading ? (
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            ) : (
              <Link
                to={user ? "/dashboard" : "/login"}
                className="btn btn-primary"
              >
                {user ? "Go to Dashboard" : "Get Started"}
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-base-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold">Why Choose Gradual?</h2>
            <p className="mt-4 text-lg text-base-content/70">
              Discover the features that make Gradual your perfect growth
              companion
            </p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="card bg-base-200">
              <div className="card-body">
                <h3 className="card-title">Track Progress</h3>
                <p>
                  Monitor your growth journey with detailed analytics and
                  insights
                </p>
              </div>
            </div>
            {/* Feature 2 */}
            <div className="card bg-base-200">
              <div className="card-body">
                <h3 className="card-title">Set Goals</h3>
                <p>Define clear objectives and track your achievements</p>
              </div>
            </div>
            {/* Feature 3 */}
            <div className="card bg-base-200">
              <div className="card-body">
                <h3 className="card-title">Stay Motivated</h3>
                <p>Get personalized encouragement and celebrate your wins</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary text-primary-content py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold">Ready to Start Your Journey?</h2>
          <p className="mt-4 text-lg">
            Join thousands of users who are already growing with Gradual
          </p>
          <Link to="/login" className="btn btn-secondary mt-8">
            Sign Up Now
          </Link>
        </div>
      </div>
    </div>
  );
};
