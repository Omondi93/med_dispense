import API from "./api";

export const getExpiryAlerts = async()=>{

    const response =
    await API.get(
        "/api/admin/expiry-alerts"
    );

    return response.data;
};