import React, { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PlatformPage from "./pages/PlatformPage";
import ServicesPage from "./pages/ServicesPage";
import AISolverPage from "./pages/AISolverPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import AdminDashboard from "./components/AdminDashboard";
import AgentDashboard from "./pages/AgentDashboard";
import PluginMarketplace from "./pages/PluginMarketplace";
import IndustryTemplates from "./pages/IndustryTemplates";
import InsightsDashboard from "./pages/InsightsDashboard";
import Navigation from "./components/Navigation";
import MatrixChatSystem from "./components/MatrixChatSystem";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
    fetch(`${backendUrl}/api/health`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Error:", error));
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/platform" element={<PlatformPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/ai-solver" element={<AISolverPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/agents" element={<AgentDashboard />} />
          <Route path="/plugins" element={<PluginMarketplace />} />
          <Route path="/templates" element={<IndustryTemplates />} />
          <Route path="/insights" element={<InsightsDashboard />} />
        </Routes>
        
        {/* Global Chat System */}
        <MatrixChatSystem />
        
        {/* Debug info - only in local development */}
        {process.env.NODE_ENV === "development" && window.location.hostname === "localhost" && (
          <div style={{ position: "fixed", bottom: "10px", right: "10px", background: "rgba(0,0,0,0.9)", color: "#00ff00", padding: "8px 12px", fontSize: "11px", fontFamily: "monospace", zIndex: 9999, border: "1px solid #00ff00", borderRadius: "4px" }}>
            <div>Backend: {process.env.REACT_APP_BACKEND_URL}</div>
            <div>Status: {message ? "✅ " + message : "⏳ Connecting..."}</div>
          </div>
        )}
      </BrowserRouter>
    </div>
  );
}

export default App;