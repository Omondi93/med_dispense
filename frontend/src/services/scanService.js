import API from "./api";

export const getScanHistory = async () => {

    const response =
        await API.get(
            "/admin/scan-history"
        );

    return response.data;
};