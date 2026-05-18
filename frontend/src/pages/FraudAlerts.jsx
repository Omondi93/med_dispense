import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";

import { getFraudAlerts } from "../services/adminService";

function FraudAlerts() {
    const [alerts, setAlerts] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    useEffect(() => {
        fetchAlerts();
    }, []);

    const fetchAlerts = async () => {
        try {
            const data = await getFraudAlerts();

            setAlerts(data.alerts);

        } catch (err) {
            setError("Failed to load alerts");

        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>

            <h1 className="text-4xl font-bold mb-6">
                Fraud Alerts
            </h1>

            {loading && (
                <p>Loading...</p>
            )}

            {error && (
                <p className="text-red-500">
                    {error}
                </p>
            )}

            {!loading && alerts.length === 0 && (
                <p>No fraud alerts found.</p>
            )}

            {!loading && alerts.length > 0 && (
                <div className="bg-white rounded-xl shadow overflow-hidden">

                    <table className="w-full">

                        <thead className="bg-black text-white">

                            <tr>
                                <th className="p-4 text-left">Batch ID</th>
                                <th className="p-4 text-left">Status</th>
                                <th className="p-4 text-left">Scan Count</th>
                                <th className="p-4 text-left">Time</th>
                            </tr>

                        </thead>

                        <tbody>

                            {alerts.map((alert, index) => (
                                <tr
                                    key={index}
                                    className="border-b"
                                >
                                    <td className="p-4">
                                        {alert.batch_id}
                                    </td>

                                    <td className="p-4 text-red-500 font-bold">
                                        {alert.status}
                                    </td>

                                    <td className="p-4">
                                        {alert.scan_count || "N/A"}
                                    </td>

                                    <td className="p-4">
                                        {alert.scanned_at || "Unknown"}
                                    </td>
                                </tr>
                            ))}

                        </tbody>

                    </table>

                </div>
            )}

        </DashboardLayout>
    );
}

export default FraudAlerts;