import { useState } from "react";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function DashboardLayout({ children }) {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-gray-100">
            <Topbar
                onMenuClick={() => setSidebarOpen(true)}
            />

            <div className="flex">
                <Sidebar
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                />

                <main className="flex-1 p-4 md:p-6 overflow-x-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default DashboardLayout;