import API from "./api";

export const generateQRCode = async (payload) => {

    const response = await API.post(
        "/qr/generate",
        payload
    );

    return response.data;
};