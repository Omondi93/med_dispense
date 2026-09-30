import API from "./api";

export const getFraudAlerts = async () => {
    const response = await API.get("/api/admin/fraud-alerts");

    return response.data;
};