function Topbar() {
    const role = localStorage.getItem("role");

    return (
        <div className="h-16 bg-white shadow flex items-center justify-between px-6">

            <h2 className="text-2xl font-bold">
                Admin Panel
            </h2>

            <div>
                Role: <span className="font-bold">{role}</span>
            </div>

        </div>
    );
}

export default Topbar;