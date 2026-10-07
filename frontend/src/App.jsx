import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import FraudAlerts from "./pages/FraudAlerts";
import BatchStats from "./pages/BatchStats";
import QRGenerator from "./pages/QRGenerator";
import QRScanner from "./pages/QRScanner";
import ScanHistory from "./pages/ScanHistory";
import Batches from "./pages/Batches";
import Medicines from "./pages/Medicines";
import QRRegistry from "./pages/QRRegistry";
import FraudAnalytics from "./pages/FraudAnalytics";
import ProtectedRoute from "./components/ProtectedRoute";
import QRScanHistory from "./pages/QRScanHistory";
import ExpiryAlerts from "./pages/ExpiryAlerts";
import PackageTraceability from "./pages/PackageTraceability";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/medicines"
          element={
            <ProtectedRoute>
              <Medicines />
            </ProtectedRoute>
          }
        />

        <Route
          path="/expiry-alerts"
          element={
            <ProtectedRoute>
              <ExpiryAlerts />
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
          path="/fraud-analytics"
          element={
            <ProtectedRoute>
              <FraudAnalytics />
            </ProtectedRoute>
          }
        />

        <Route
          path="/batches"
          element={
            <ProtectedRoute>
              <Batches />
            </ProtectedRoute>
          }
        />

        <Route
          path="/packages"
          element={
            <ProtectedRoute>
              <PackageTraceability />
            </ProtectedRoute>
          }
        />

        <Route
          path="/scan-history"
          element={
            <ProtectedRoute>
              <ScanHistory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scanner"
          element={
            <ProtectedRoute>
              <QRScanner />
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

        <Route
          path="/qr-registry"
          element={
            <ProtectedRoute>
              <QRRegistry />
            </ProtectedRoute>
          }
        />

        <Route
          path="/qr-registry/:qrId/history"
          element={
            <ProtectedRoute>
              <QRScanHistory />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;