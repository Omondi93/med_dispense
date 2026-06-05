import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";
import { getFraudSummary } from "../services/fraudService";

function FraudAnalytics() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadSummary();
    }, []);

    const loadSummary = async () => {
        try {
            const response = await getFraudSummary();
            setSummary(response.data);
        } catch (error) {
            console.log(error.response?.data || error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <p>Loading fraud analytics...</p>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                Fraud Analytics
            </h1>

            <div className="grid grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow">
                    <h2>Total QRs</h2>
                    <p className="text-3xl font-bold">
                        {summary?.total_qrs || 0}
                    </p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow">
                    <h2>Flagged QRs</h2>
                    <p className="text-3xl font-bold text-red-600">
                        {summary?.flagged_qrs || 0}
                    </p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow">
                    <h2>Cloned Scans</h2>
                    <p className="text-3xl font-bold text-orange-600">
                        {summary?.cloned_scans || 0}
                    </p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow">
                    <h2>Tampered Scans</h2>
                    <p className="text-3xl font-bold text-red-700">
                        {summary?.tampered_scans || 0}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow">
                    <h2 className="text-2xl font-bold mb-4">
                        Most Scanned QR Codes
                    </h2>

                    <table className="w-full">
                        <thead>
                            <tr>
                                <th>QR ID</th>
                                <th>Batch</th>
                                <th>Scans</th>
                                <th>Flagged</th>
                            </tr>
                        </thead>

                        <tbody>
                            {summary?.most_scanned?.map((qr) => (
                                <tr key={qr.id} className="border-b">
                                    <td>{qr.id}</td>
                                    <td>{qr.batch_id}</td>
                                    <td>{qr.scan_count}</td>
                                    <td>{qr.is_flagged ? "Yes" : "No"}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="bg-white p-6 rounded-xl shadow">
                    <h2 className="text-2xl font-bold mb-4">
                        Flagged QR Codes
                    </h2>

                    <table className="w-full">
                        <thead>
                            <tr>
                                <th>QR ID</th>
                                <th>Batch</th>
                                <th>Scans</th>
                                <th>Signature</th>
                            </tr>
                        </thead>

                        <tbody>
                            {summary?.flagged_list?.map((qr) => (
                                <tr key={qr.id} className="border-b">
                                    <td>{qr.id}</td>
                                    <td>{qr.batch_id}</td>
                                    <td>{qr.scan_count}</td>
                                    <td>{qr.signature}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </DashboardLayout>
    );
}

export default FraudAnalytics;