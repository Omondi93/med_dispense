import API from "./api";

export const getFraudSummary = async () => {
    const response = await API.get("/admin/fraud-summary");
    return response.data;
};