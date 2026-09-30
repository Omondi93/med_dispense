import API from "./api";


// CREATE MEDICINE

export const createMedicine =
    async (data) => {

        const response =
            await API.post(

                "/api/medicine/",

                data

            );

        return response.data;

    };


// GET MEDICINES

export const getMedicines =
    async () => {

        const response =
            await API.get(

                "/medicine/"

            );

        return response.data;

    };