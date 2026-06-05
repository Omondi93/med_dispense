import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";

import {
    createBatch,
    getBatches
} from "../services/batchService";

import {
    getMedicines
} from "../services/medicineService";


function Batches() {

    const [batches, setBatches] = useState([]);
    const [medicines, setMedicines] = useState([]);

    const [formData, setFormData] = useState({
        batch_number: "",
        medicine_id: "",
        manufacture_date: "",
        expiry_date: "",
        quantity: ""
    });

    useEffect(() => {
        loadBatches();
        loadMedicines();
    }, []);

    const loadBatches = async () => {
        try {
            const response = await getBatches();
            setBatches(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        }
    };

    const loadMedicines = async () => {
        try {
            const response = await getMedicines();
            setMedicines(response.data || []);
        } catch (error) {
            console.log(error.response?.data || error);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            await createBatch(formData);

            setFormData({
                batch_number: "",
                medicine_id: "",
                manufacture_date: "",
                expiry_date: "",
                quantity: ""
            });

            await loadBatches();

        } catch (error) {
            console.log(error.response?.data || error);
            alert(error.response?.data?.error || "Batch creation failed");
        }
    };

    return (
        <DashboardLayout>
            <h1 className="text-4xl font-bold mb-6">
                Batch Management
            </h1>

            <div className="bg-white p-6 rounded-xl shadow mb-8">
                <form
                    onSubmit={handleSubmit}
                    className="grid grid-cols-2 gap-4"
                >
                    <input
                        name="batch_number"
                        placeholder="Batch Number"
                        value={formData.batch_number}
                        onChange={handleChange}
                        className="border p-3 rounded"
                    />

                    <select
                        name="medicine_id"
                        value={formData.medicine_id}
                        onChange={handleChange}
                        className="border p-3 rounded"
                    >
                        <option value="">
                            Select Medicine
                        </option>

                        {medicines.map((medicine) => (
                            <option
                                key={medicine.id}
                                value={medicine.id}
                            >
                                {medicine.name}
                            </option>
                        ))}
                    </select>

                    <input
                        type="date"
                        name="manufacture_date"
                        value={formData.manufacture_date}
                        onChange={handleChange}
                        className="border p-3 rounded"
                    />

                    <input
                        type="date"
                        name="expiry_date"
                        value={formData.expiry_date}
                        onChange={handleChange}
                        className="border p-3 rounded"
                    />

                    <input
                        name="quantity"
                        placeholder="Quantity"
                        value={formData.quantity}
                        onChange={handleChange}
                        className="border p-3 rounded"
                    />

                    <button
                        type="submit"
                        className="bg-black text-white p-3 rounded"
                    >
                        Create Batch
                    </button>
                </form>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
                <table className="w-full">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Batch</th>
                            <th>Medicine</th>
                            <th>Quantity</th>
                            <th>Expiry</th>
                        </tr>
                    </thead>

                    <tbody>
                        {batches.map((batch) => (
                            <tr
                                key={batch.id}
                                className="border-b"
                            >
                                <td>{batch.id}</td>
                                <td>{batch.batch_number}</td>
                                <td>{batch.medicine_name || batch.medicine_id}</td>
                                <td>{batch.quantity}</td>
                                <td>{batch.expiry_date}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </DashboardLayout>
    );
}

export default Batches;