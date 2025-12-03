// src/App.jsx
import React, { useContext, useEffect, useState } from "react";
import { AuthProvider, AuthContext } from "./contexts/AuthContext";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/SignupForm";
import UserDashboard from "./components/UserDashboard";

import "./App.css"; // <-- NEW

const MAX_USERS = 50;

const AppContent = () => {
  const { token, logout } = useContext(AuthContext);
  const [userCount, setUserCount] = useState(null);

  // Fetch user count for homepage
  useEffect(() => {
    const fetchUserCount = async () => {
      try {
        const res = await fetch("http://192.168.0.75:8020/auth/user/count");
        const data = await res.json();
        setUserCount(data.count);
      } catch (err) {
        console.error("Failed to fetch user count:", err);
      }
    };

    fetchUserCount();
  }, []);

  // If user not logged in → show landing
  if (!token) {
    return (
      <div className="landing-container">
        <h1 className="landing-title">Scene Sense</h1>

        {userCount !== null && (
          <p className="user-count">
            {userCount} / {MAX_USERS} registered users
          </p>
        )}

        <div className="form-block">
          <SignupForm />
        </div>

        <div className="divider"></div>

        <div className="form-block">
          <LoginForm />
        </div>
      </div>
    );
  }

  // Logged in → dashboard
  return <UserDashboard logout={logout} />;
};

const App = () => (
  <AuthProvider>
    <AppContent />
  </AuthProvider>
);

export default App;
