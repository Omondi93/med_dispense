import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import { getScanHistoryByQR } from "../services/scanHistoryService";

function QRScanHistory() {
    const { qrId } = useParams();
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadHistory();
    }, [qrId]);

    const loadHistory = async () => {
        try {
            const response = await getScanHistoryByQR(qrId);
            setLogs(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                QR Scan History
            </h1>

            <p className="mb-6">
                QR ID: <strong>{qrId}</strong>
            </p>

            {loading ? (
                <p>Loading scan history...</p>
            ) : (
                <div className="overflow-x-auto">
                    {logs.length === 0 ? (
                        <p>No scan history found for this QR.</p>
                    ) : (
                        <table className="min-w-full">
                            <thead>
                                <tr>
                                    <th>Status</th>
                                    <th>Valid</th>
                                    <th>Scan Count</th>
                                    <th>IP</th>
                                    <th>Time</th>
                                </tr>
                            </thead>

                            <tbody>
                                {logs.map((log) => (
                                    <tr key={log.id} className="border-b">
                                        <td>{log.status}</td>
                                        <td>{log.is_valid ? "Yes" : "No"}</td>
                                        <td>{log.scan_count}</td>
                                        <td>{log.ip_address || "N/A"}</td>
                                        <td>{log.scanned_at}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </DashboardLayout>
    );
}

export default QRScanHistory;