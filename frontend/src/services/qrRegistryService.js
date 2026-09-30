import API from "./api";

export const getQRRegistry = async () => {
    const response = await API.get("/api/admin/qr-registry");
    return response.data;
};