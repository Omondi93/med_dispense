import API from "./api";

export const getFraudSummary = async () => {
    const response = await API.get("/api/admin/fraud-summary");
    return response.data;
};