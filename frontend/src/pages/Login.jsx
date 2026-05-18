import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginUser } from "../services/authService";

function Login() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const [error, setError] = useState("");

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleLogin = async (e) => {
        e.preventDefault();

        try {
            const data = await loginUser(
                formData.email,
                formData.password
            );

            // Store token + role
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("role", data.role);

            navigate("/dashboard");

        } catch (err) {
            setError(
                err.response?.data?.error || "Login failed"
            );
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <form
                onSubmit={handleLogin}
                className="bg-white p-8 rounded-xl shadow-lg w-96"
            >
                <h1 className="text-3xl font-bold mb-6 text-center">
                    MED DISPENSE
                </h1>

                {error && (
                    <p className="text-red-500 mb-4">
                        {error}
                    </p>
                )}

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    className="w-full border p-3 mb-4 rounded-lg"
                    onChange={handleChange}
                />

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    className="w-full border p-3 mb-4 rounded-lg"
                    onChange={handleChange}
                />

                <button
                    type="submit"
                    className="w-full bg-black text-white p-3 rounded-lg"
                >
                    Login
                </button>
            </form>
        </div>
    );
}

export default Login;