import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import DashboardLayout from "../layouts/DashboardLayout";

const API = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL });
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default function PackageTraceability() {
  const [packages, setPackages] = useState([]);
  const [batchId, setBatchId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [childQuantities, setChildQuantities] = useState("");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [lastQRs, setLastQRs] = useState([]);
  const [trace, setTrace] = useState(null);

  const loadPackages = useCallback(async () => {
    try {
      const response = await API.get("/api/packages");
      setPackages(response.data.data || []);
    } catch (error) {
      setMessage(error.response?.data?.error || "Could not load packages. Check API URL and login.");
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchPackages = async () => {
        try {
            const response = await API.get("/api/packages");

            if (!cancelled) {
                setPackages(response.data.data || []);
            }
        } catch (error) {
            if (!cancelled) {
                setMessage(
                    error.response?.data?.error ||
                    "Could not load packages. Check API URL and login."
                );
            }
        }
    };

    fetchPackages();

    return () => {
        cancelled = true;
    };
}, []);

  const initialize = async (event) => {
    event.preventDefault(); setBusy(true); setMessage(""); setLastQRs([]); setTrace(null);
    try {
      const response = await API.post("/api/packages/initialize", { batch_id: Number(batchId), quantity: Number(quantity) });
      setMessage(response.data.message);
      setLastQRs([{ ...response.data.data, qr_code: response.data.qr_code, qr_payload: response.data.qr_payload }]);
      setBatchId(""); setQuantity(""); await loadPackages();
    } catch (error) { setMessage(error.response?.data?.error || "Package creation failed."); }
    finally { setBusy(false); }
  };

  const split = async (event) => {
    event.preventDefault(); setBusy(true); setMessage(""); setLastQRs([]); setTrace(null);
    const quantities = childQuantities.split(",").map((part) => Number(part.trim()));
    try {
      const response = await API.post(`/api/packages/${Number(sourceId)}/split`, { quantities, notes });
      setMessage(response.data.message);
      setLastQRs(response.data.children || []);
      setSourceId(""); setChildQuantities(""); setNotes(""); await loadPackages();
    } catch (error) { setMessage(error.response?.data?.error || "Split failed. Confirm quantities equal the source package quantity."); }
    finally { setBusy(false); }
  };

  const showTrace = async (id) => {
    setMessage("");
    try { const response = await API.get(`/api/packages/${id}/trace`); setTrace(response.data); }
    catch (error) { setMessage(error.response?.data?.error || "Could not retrieve trace."); }
  };

  return (
    <DashboardLayout>
      <div className="p-4 md:p-6 space-y-6">
        <div><h1 className="text-2xl font-bold">Package Traceability</h1><p className="text-sm text-gray-500 mt-1">Allocate batch stock to QR-identified packages, split packages, and inspect their lineage.</p></div>
        {message && <div role="status" className="rounded-lg border p-3 text-sm">{message}</div>}
        <div className="grid lg:grid-cols-2 gap-5">
          <form onSubmit={initialize} className="border rounded-xl p-4 space-y-3">
            <h2 className="font-semibold text-lg">Create original package</h2>
            <p className="text-sm text-gray-500">The allocated quantity is reserved from the batch. You cannot allocate more than the batch quantity.</p>
            <label className="block text-sm">Batch ID<input required type="number" min="1" value={batchId} onChange={(e) => setBatchId(e.target.value)} className="mt-1 w-full border rounded-lg p-2" /></label>
            <label className="block text-sm">Quantity inside package<input required type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} className="mt-1 w-full border rounded-lg p-2" /></label>
            <button disabled={busy} className="rounded-lg bg-black text-white px-4 py-2 disabled:opacity-50">Create package and QR</button>
          </form>
          <form onSubmit={split} className="border rounded-xl p-4 space-y-3">
            <h2 className="font-semibold text-lg">Split an active package</h2>
            <p className="text-sm text-gray-500">Enter child quantities separated by commas. Their sum must equal the source package quantity.</p>
            <label className="block text-sm">Source package ID<input required type="number" min="1" value={sourceId} onChange={(e) => setSourceId(e.target.value)} className="mt-1 w-full border rounded-lg p-2" /></label>
            <label className="block text-sm">Child quantities<input required placeholder="e.g. 50, 30, 20" value={childQuantities} onChange={(e) => setChildQuantities(e.target.value)} className="mt-1 w-full border rounded-lg p-2" /></label>
            <label className="block text-sm">Notes (optional)<input maxLength="500" value={notes} onChange={(e) => setNotes(e.target.value)} className="mt-1 w-full border rounded-lg p-2" /></label>
            <button disabled={busy} className="rounded-lg bg-black text-white px-4 py-2 disabled:opacity-50">Record split</button>
          </form>
        </div>

        {lastQRs.length > 0 && <section className="border rounded-xl p-4"><h2 className="font-semibold text-lg mb-3">New package QR codes</h2><div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{lastQRs.map((item) => <div key={item.id} className="border rounded-lg p-3"><img className="w-40 h-40 mx-auto" alt={`QR for package ${item.serial_number}`} src={`data:image/png;base64,${item.qr_code}`} /><p className="font-medium break-all">{item.serial_number}</p><p className="text-sm">Package ID: {item.id} · Quantity: {item.quantity}</p><button type="button" onClick={() => navigator.clipboard.writeText(item.qr_payload)} className="mt-2 underline text-sm">Copy QR payload</button></div>)}</div></section>}

        <section className="border rounded-xl p-4"><div className="flex items-center justify-between gap-3 mb-3"><h2 className="font-semibold text-lg">Registered packages</h2><button onClick={loadPackages} className="underline text-sm">Refresh</button></div><div className="overflow-x-auto"><table className="w-full text-sm text-left"><thead><tr className="border-b"><th className="p-2">Package ID</th><th className="p-2">Batch</th><th className="p-2">Quantity</th><th className="p-2">Status</th><th className="p-2">Parent</th><th className="p-2">Trace</th></tr></thead><tbody>{packages.map((p) => <tr key={p.id} className="border-b"><td className="p-2">{p.id}<div className="text-xs text-gray-500 break-all">{p.serial_number}</div></td><td className="p-2">{p.batch_number} (#{p.batch_id})</td><td className="p-2">{p.quantity}</td><td className="p-2">{p.status}</td><td className="p-2">{p.parent_package_id ?? "Original"}</td><td className="p-2"><button onClick={() => showTrace(p.id)} className="underline">View</button></td></tr>)}</tbody></table>{packages.length === 0 && <p className="text-sm text-gray-500 py-4">No traceable packages yet.</p>}</div></section>
        {trace && <section className="border rounded-xl p-4"><div className="flex justify-between"><h2 className="font-semibold text-lg">Package lineage</h2><button onClick={() => setTrace(null)} className="underline text-sm">Close</button></div><pre className="mt-3 whitespace-pre-wrap break-words text-xs">{JSON.stringify(trace, null, 2)}</pre></section>}
      </div>
    </DashboardLayout>
  );
}
