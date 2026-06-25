import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import { getQRRegistry } from "../services/qrRegistryService";

function QRRegistry() {
    const [qrs, setQrs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadRegistry();
    }, []);

    const loadRegistry = async () => {
        try {
            const response = await getQRRegistry();
            setQrs(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                QR Registry
            </h1>

            {loading ? (
                <p>Loading QR registry...</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Batch</th>
                                <th>Serial</th>
                                <th>Signature</th>
                                <th>Scans</th>
                                <th>Flagged</th>
                                <th>Created</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            {qrs.map((qr) => (
                                <tr key={qr.id} className="border-b">
                                    <td>{qr.id}</td>
                                    <td>{qr.batch_id}</td>
                                    <td>{qr.serial_number || "N/A"}</td>
                                    <td>{qr.signature}</td>
                                    <td>{qr.scan_count}</td>
                                    <td>{qr.is_flagged ? "Yes" : "No"}</td>
                                    <td>{qr.created_at}</td>
                                    <td>
                                        <Link
                                            to={`/qr-registry/${qr.id}/history`}
                                            className="text-blue-600 underline"
                                        >
                                            View History
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {qrs.length === 0 && (
                        <p className="mt-4">
                            No QR codes generated yet.
                        </p>
                    )}
                </div>
            )}
        </DashboardLayout>
    );
}

export default QRRegistry;