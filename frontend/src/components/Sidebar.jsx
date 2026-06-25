import { Link, useNavigate } from "react-router-dom";

function Sidebar({ isOpen, onClose }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("role");

        navigate("/");
    };

    const linkClass =
        "block py-2 px-3 rounded-lg hover:bg-gray-800 transition-colors text-sm";

    return (
        <>
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={onClose}
                />
            )}

            <aside
                className={`
                    fixed md:static
                    top-0 left-0
                    z-50
                    w-64
                    h-screen
                    bg-black
                    text-white
                    p-5
                    overflow-y-auto
                    overscroll-contain
                    transform
                    transition-transform
                    duration-300
                    ${isOpen ? "translate-x-0" : "-translate-x-full"}
                    md:translate-x-0
                `}
            >
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">
                        MED DISPENSE
                    </h1>

                    <button
                        onClick={onClose}
                        className="md:hidden text-3xl"
                    >
                        ×
                    </button>
                </div>

                <nav className="flex flex-col gap-1 pb-24">
                    <Link
                        to="/dashboard"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Dashboard
                    </Link>

                    <Link
                        to="/scanner"
                        onClick={onClose}
                        className={linkClass}
                    >
                        QR Scanner
                    </Link>

                    <Link
                        to="/medicines"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Medicine Management
                    </Link>

                    <Link
                        to="/scan-history"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Scan History
                    </Link>

                    <Link
                        to="/batches"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Batch Management
                    </Link>

                    <Link
                        to="/fraud-alerts"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Fraud Alerts
                    </Link>

                    <Link
                        to="/fraud-analytics"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Fraud Analytics
                    </Link>

                    <Link
                        to="/expiry-alerts"
                        onClick={onClose}
                        className={linkClass}
                    >
                        Expiry Alerts
                    </Link>

                    <Link
                        to="/qr-generator"
                        onClick={onClose}
                        className={linkClass}
                    >
                        QR Generator
                    </Link>

                    <Link
                        to="/qr-registry"
                        onClick={onClose}
                        className={linkClass}
                    >
                        QR Registry
                    </Link>

                    <button
                        onClick={handleLogout}
                        className="mt-6 bg-red-600 hover:bg-red-700 transition-colors p-3 rounded-lg text-sm"
                    >
                        Logout
                    </button>
                </nav>
            </aside>
        </>
    );
}

export default Sidebar;