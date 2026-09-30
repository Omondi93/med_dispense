import API from "./api";

export const getFraudAnalytics = async () => {
    const response = await API.get(
        "/api/admin/fraud-analytics"
    );

    return response.data;
};
export const getDashboardStats = async () => {
    const response = await API.get("/api/admin/dashboard-stats");

    return response.data;
};