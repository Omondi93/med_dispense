import { useEffect, useState } from "react";

import {
  PieChart,
  Pie,
  Tooltip,
  Cell,
  ResponsiveContainer
} from "recharts";

import DashboardLayout from "../layouts/DashboardLayout";

import {
  getDashboardStats,
  getFraudAnalytics
} from "../services/dashboardService";


function Dashboard() {

  const [stats, setStats] = useState({
    total_scans: 0,
    fraud_alerts: 0,
    active_batches: 0
  });

  const [analytics, setAnalytics] = useState([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {

    try {

      const statsData = await getDashboardStats();

      const analyticsData = await getFraudAnalytics();

      setStats(statsData.data);

      setAnalytics(analyticsData.data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }
  };

  return (
    <DashboardLayout>

      <h1 className="text-4xl font-bold mb-6">
        Dashboard
      </h1>

      {loading ? (

        <p>Loading dashboard...</p>

      ) : (

        <>
          {/* STAT CARDS */}
          <div className="grid grid-cols-3 gap-6 mb-10">

            <div className="bg-white p-6 rounded-xl shadow">

              <h2 className="text-xl font-bold">
                Total Scans
              </h2>

              <p className="text-4xl mt-4">
                {stats.total_scans}
              </p>

            </div>

            <div className="bg-white p-6 rounded-xl shadow">

              <h2 className="text-xl font-bold">
                Fraud Alerts
              </h2>

              <p className="text-4xl mt-4 text-red-500">
                {stats.fraud_alerts}
              </p>

            </div>

            <div className="bg-white p-6 rounded-xl shadow">

              <h2 className="text-xl font-bold">
                Active Batches
              </h2>

              <p className="text-4xl mt-4">
                {stats.active_batches}
              </p>

            </div>

          </div>

          {/* CHART */}
          <div className="bg-white p-6 rounded-xl shadow">

            <h2 className="text-2xl font-bold mb-6">
              Scan Analytics
            </h2>

            <div className="h-96">

              <ResponsiveContainer width="100%" height="100%">

                <PieChart>

                  <Pie
                    data={analytics}
                    dataKey="count"
                    nameKey="status"
                    outerRadius={150}
                    label
                  >
                    {analytics.map((entry, index) => (
                      <Cell key={index} />
                    ))}
                  </Pie>

                  <Tooltip />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>

        </>
      )}

    </DashboardLayout>
  );
}

export default Dashboard