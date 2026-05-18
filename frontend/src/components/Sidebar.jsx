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

                <Link to="/fraud-alerts">
                    Fraud Alerts
                </Link>

                <Link to="/batch-stats">
                    Batch Stats
                </Link>

                <Link to="/qr-generator">
                    QR Generator
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