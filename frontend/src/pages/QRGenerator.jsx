import { useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";

import { generateQRCode } from "../services/qrService";

function QRGenerator() {

    const [formData, setFormData] = useState({
        batch_id: "",
        medicine_id: "",
        manufacture_date: "",
        expiry_date: ""
    });

    const [qrData, setQrData] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const handleChange = (e) => {

        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });

    };

    const handleSubmit = async (e) => {

        e.preventDefault();

        setLoading(true);

        setError("");

        try {

            const data = await generateQRCode(formData);

            setQrData(data);

        } catch (err) {

            setError(
                err.response?.data?.error || "QR generation failed"
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

            {/* FORM */}
            <form
                onSubmit={handleSubmit}
                className="bg-white p-6 rounded-xl shadow mb-6"
            >

                <div className="grid grid-cols-2 gap-4">

                    <input
                        type="number"
                        name="batch_id"
                        placeholder="Batch ID"
                        className="border p-3 rounded-lg"
                        onChange={handleChange}
                    />

                    <input
                        type="number"
                        name="medicine_id"
                        placeholder="Medicine ID"
                        className="border p-3 rounded-lg"
                        onChange={handleChange}
                    />

                    <input
                        type="date"
                        name="manufacture_date"
                        className="border p-3 rounded-lg"
                        onChange={handleChange}
                    />

                    <input
                        type="date"
                        name="expiry_date"
                        className="border p-3 rounded-lg"
                        onChange={handleChange}
                    />

                </div>

                <button
                    type="submit"
                    className="mt-6 bg-black text-white px-6 py-3 rounded-lg"
                >
                    {loading ? "Generating..." : "Generate QR"}
                </button>

            </form>

            {/* ERROR */}
            {error && (
                <div className="bg-red-100 text-red-500 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}

            {/* QR RESULT */}
            {qrData && (

                <div className="bg-white p-6 rounded-xl shadow">

                    <h2 className="text-2xl font-bold mb-4">
                        Generated QR Code
                    </h2>

                    {/* QR IMAGE */}
                    <img
                        src={`data:image/png;base64,${qrData.qr_code}`}
                        alt="QR Code"
                        className="w-64 h-64 border"
                    />

                    {/* PAYLOAD */}
                    <div className="mt-6">

                        <h3 className="font-bold mb-2">
                            Payload
                        </h3>

                        <p className="break-all bg-gray-100 p-3 rounded-lg text-sm">
                            {qrData.payload}
                        </p>

                    </div>

                    {/* DOWNLOAD */}
                    <a
                        href={`data:image/png;base64,${qrData.qr_code}`}
                        download={`qr_batch_${formData.batch_id}.png`}
                        className="inline-block mt-6 bg-green-600 text-white px-6 py-3 rounded-lg"
                    >
                        Download QR
                    </a>

                </div>

            )}

        </DashboardLayout>
    );
}

export default QRGenerator;