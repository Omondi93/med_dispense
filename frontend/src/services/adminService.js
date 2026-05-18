import API from "./api";

export const getFraudAlerts = async () => {
    const response = await API.get("/admin/fraud-alerts");

    return response.data;
};