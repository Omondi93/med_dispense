import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";

import { getBatches } from "../services/batchService";
import { generateQRCode } from "../services/qrService";


function QRGenerator() {
    const [batches, setBatches] = useState([]);
    const [batchId, setBatchId] = useState("");
    const [qrData, setQrData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        loadBatches();
    }, []);

    const loadBatches = async () => {
        try {
            const response = await getBatches();
            setBatches(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!batchId) {
            setError("Please select a batch");
            return;
        }

        try {
            setLoading(true);
            setError("");

            const response = await generateQRCode({
                batch_id: batchId
            });

            setQrData(response);

        } catch (error) {
            setError(
                error.response?.data?.error ||
                "QR generation failed"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                QR Generator
            </h1>

            <form
                onSubmit={handleSubmit}
                className="bg-white p-6 rounded-xl shadow mb-6"
            >
                <label className="block mb-2 font-bold">
                    Select Batch
                </label>

                <select
                    value={batchId}
                    onChange={(e) => setBatchId(e.target.value)}
                    className="border p-3 rounded w-full mb-4"
                >
                    <option value="">
                        Select Batch
                    </option>

                    {batches.map((batch) => (
                        <option
                            key={batch.id}
                            value={batch.id}
                        >
                            {batch.batch_number} — {batch.medicine_name || `Medicine ID ${batch.medicine_id}`}
                        </option>
                    ))}
                </select>

                <button
                    type="submit"
                    className="bg-black text-white px-6 py-3 rounded"
                >
                    {loading ? "Generating..." : "Generate QR"}
                </button>
            </form>

            {error && (
                <div className="bg-red-100 text-red-600 p-4 rounded mb-6">
                    {error}
                </div>
            )}

            {qrData && (
                <div className="bg-white p-6 rounded-xl shadow">
                    <h2 className="text-2xl font-bold mb-4">
                        Generated QR Code
                    </h2>

                    <img
                        src={`data:image/png;base64,${qrData.qr_code}`}
                        alt="QR Code"
                        className="w-64 h-64 border mb-6"
                    />

                    <p>
                        <strong>Batch ID:</strong> {qrData.batch_id}
                    </p>

                    <p>
                        <strong>Medicine ID:</strong> {qrData.medicine_id}
                    </p>

                    <p>
                        <strong>Manufacture Date:</strong> {qrData.manufacture_date}
                    </p>

                    <p>
                        <strong>Expiry Date:</strong> {qrData.expiry_date}
                    </p>

                    <div className="mt-4">
                        <h3 className="font-bold mb-2">
                            Payload
                        </h3>

                        <p className="break-all bg-gray-100 p-3 rounded text-sm">
                            {qrData.payload}
                        </p>
                    </div>

                    <a
                        href={`data:image/png;base64,${qrData.qr_code}`}
                        download={`qr_batch_${qrData.batch_id}.png`}
                        className="inline-block mt-6 bg-green-600 text-white px-6 py-3 rounded"
                    >
                        Download QR
                    </a>
                </div>
            )}
        </DashboardLayout>
    );
}

export default QRGenerator;