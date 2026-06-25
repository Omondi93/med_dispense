import { useEffect, useState }
    from "react";

import DashboardLayout
    from "../layouts/DashboardLayout";

import {

    createMedicine,
    getMedicines

}
    from "../services/medicineService";


function Medicines() {

    const [medicines, setMedicines]
        = useState([]);

    const [name, setName]
        = useState("");


    useEffect(() => {

        loadMedicines();

    }, []);


    const loadMedicines =
        async () => {

            try {

                const response =
                    await getMedicines();

                setMedicines(
                    response.data || []
                );

            }

            catch (error) {

                console.log(error);

            }

        };


    const handleSubmit =
        async (e) => {

            e.preventDefault();

            try {

                await createMedicine({

                    name: name

                });

                setName("");

                await loadMedicines();

            }

            catch (error) {

                console.log(
                    error.response?.data
                );

            }

        };


    return (

        <DashboardLayout>

            <h1 className="text-4xl font-bold mb-6">

                Medicine Management

            </h1>


            <div className="bg-white p-6 rounded-xl shadow mb-8">

                <form
                    onSubmit={handleSubmit}
                    className="space-y-4"
                >

                    <input

                        type="text"

                        placeholder="Medicine Name"

                        value={name}

                        onChange={(e) =>
                            setName(
                                e.target.value
                            )}

                        className="border p-3 rounded w-full"

                    />


                    <button
                        type="submit"
                        className="bg-black text-white p-3 rounded"
                    >

                        Create Medicine

                    </button>

                </form>

            </div>


            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr>

                            <th>ID</th>

                            <th>Name</th>

                            <th>Manufacturer</th>

                        </tr>

                    </thead>

                    <tbody>

                        {
                            medicines.map(
                                (medicine) => (

                                    <tr
                                        key={medicine.id}
                                        className="border-b"
                                    >

                                        <td>

                                            {medicine.id}

                                        </td>

                                        <td>

                                            {medicine.name}

                                        </td>

                                        <td>

                                            {medicine.manufacturer_id}

                                        </td>

                                    </tr>

                                ))
                        }

                    </tbody>

                </table>

            </div>

        </DashboardLayout>

    )

}

export default Medicines;