import { Link, useNavigate } from "react-router-dom";

function Sidebar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("role");

        navigate("/");
    };

    return (
        <div className="w-64 min-h-screen bg-black text-white p-5">

            <h1 className="text-2xl font-bold mb-10">
                MED DISPENSE
            </h1>

            <nav className="flex flex-col gap-4">

                <Link to="/dashboard">
                    Dashboard
                </Link>

                <Link to="/scanner">
                    QR Scanner
                </Link>

                <Link to="/medicines">
                    Medicine Management
                </Link>

                <Link to="/scan-history">
                    Scan History
                </Link>

                <Link to="/batches">
                    Batch Management
                </Link>

                <Link to="/fraud-alerts">
                    Fraud Alerts
                </Link>

                <Link to="/fraud-analytics">
                    Fraud Analytics
                </Link>

                <Link to="/expiry-alerts">
                    Expiry Alerts
                </Link>

                <Link to="/qr-generator">
                    QR Generator
                </Link>

                <Link to="/qr-registry">
                    QR Registry
                </Link>

                <button
                    onClick={handleLogout}
                    className="mt-10 bg-red-500 p-2 rounded-lg"
                >
                    Logout
                </button>

            </nav>
        </div>
    );
}

export default Sidebar;