import API from "./api";


// CREATE BATCH

export const createBatch =
    async (data) => {

        const response =
            await API.post(

                "/batch/",

                data

            );

        return response.data;

    };


// GET BATCHES

export const getBatches =
    async () => {

        const response =
            await API.get(

                "/batch/"

            );

        return response.data;

    };