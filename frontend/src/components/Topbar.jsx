function Topbar({ onMenuClick }) {
    const role = localStorage.getItem("role");

    return (
        <div className="h-16 bg-white shadow flex items-center justify-between px-4 md:px-6">
            <button
                onClick={onMenuClick}
                className="md:hidden bg-black text-white px-3 py-2 rounded"
            >
                ☰
            </button>

            <h2 className="text-lg md:text-2xl font-bold">
                MED DISPENSE
            </h2>

            <div className="text-sm md:text-base">
                Role: <span className="font-bold">{role}</span>
            </div>
        </div>
    );
}

export default Topbar;