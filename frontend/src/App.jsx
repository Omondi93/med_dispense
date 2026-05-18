import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import FraudAlerts from "./pages/FraudAlerts";
import BatchStats from "./pages/BatchStats";
import QRGenerator from "./pages/QRGenerator";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Login />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/fraud-alerts"
          element={
            <ProtectedRoute>
              <FraudAlerts />
            </ProtectedRoute>
          }
        />

        <Route
          path="/batch-stats"
          element={
            <ProtectedRoute>
              <BatchStats />
            </ProtectedRoute>
          }
        />

        <Route
          path="/qr-generator"
          element={
            <ProtectedRoute>
              <QRGenerator />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;