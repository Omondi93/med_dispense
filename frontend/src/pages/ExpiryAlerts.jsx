import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";
import { getExpiryAlerts } from "../services/expiryService";

function ExpiryAlerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAlerts();
    }, []);

    const loadAlerts = async () => {
        try {
            const response = await getExpiryAlerts();
            setAlerts(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusClass = (status) => {
        if (status === "expired") {
            return "text-red-600 font-bold";
        }

        if (status === "critical") {
            return "text-orange-600 font-bold";
        }

        return "text-yellow-600 font-bold";
    };

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                Expiry Alerts
            </h1>

            {loading ? (
                <p>Loading expiry alerts...</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead>
                            <tr>
                                <th>Batch</th>
                                <th>Medicine</th>
                                <th>Expiry Date</th>
                                <th>Days Remaining</th>
                                <th>Status</th>
                            </tr>
                        </thead>

                        <tbody>
                            {alerts.map((alert) => (
                                <tr
                                    key={alert.id}
                                    className="border-b"
                                >
                                    <td>{alert.batch_number}</td>
                                    <td>{alert.medicine_name || "N/A"}</td>
                                    <td>{alert.expiry_date}</td>
                                    <td>{alert.days_remaining}</td>
                                    <td className={getStatusClass(alert.status)}>
                                        {alert.status}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {alerts.length === 0 && (
                        <p className="mt-4">
                            No expired or near-expiry batches found.
                        </p>
                    )}
                </div>
            )}
        </DashboardLayout>
    );
}

export default ExpiryAlerts;