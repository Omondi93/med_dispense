import API from "./api";

export const getScanHistoryByQR = async (qrId) => {
    const response = await API.get(`/admin/scan-history/${qrId}`);
    return response.data;
};