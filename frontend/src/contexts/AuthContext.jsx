// src/contexts/AuthContext.jsx
import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
      setIsAdmin(false);
    }
  }, [token]);

  const logout = () => {
    setToken("");
  };

  return (
    <AuthContext.Provider value={{ token, setToken, isAdmin, setIsAdmin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
