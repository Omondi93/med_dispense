import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { registerUser } from "../services/authService";

function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
    });

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleRegister = async (e) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        try {
            setLoading(true);

            await registerUser(
                formData.name,
                formData.email,
                formData.password
            );

            setSuccess("Registration successful. You can now log in.");

            setTimeout(() => {
                navigate("/");
            }, 1500);

        } catch (err) {
            setError(
                err.response?.data?.error || "Registration failed"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <form
                onSubmit={handleRegister}
                className="bg-white p-8 rounded-xl shadow-lg w-96"
            >
                <h1 className="text-3xl font-bold mb-6 text-center">
                    Create Account
                </h1>

                {error && (
                    <p className="text-red-500 mb-4">
                        {error}
                    </p>
                )}

                {success && (
                    <p className="text-green-600 mb-4">
                        {success}
                    </p>
                )}

                <input
                    type="text"
                    name="name"
                    placeholder="Manufacturer Name"
                    className="w-full border p-3 mb-4 rounded-lg"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    className="w-full border p-3 mb-4 rounded-lg"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    className="w-full border p-3 mb-4 rounded-lg"
                    value={formData.password}
                    onChange={handleChange}
                    required
                />

                <input
                    type="password"
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    className="w-full border p-3 mb-4 rounded-lg"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-black text-white p-3 rounded-lg"
                >
                    {loading ? "Creating Account..." : "Register"}
                </button>

                <p className="text-center mt-4 text-sm">
                    Already have an account?{" "}
                    <button
                        type="button"
                        onClick={() => navigate("/")}
                        className="text-blue-600 hover:underline"
                    >
                        Login
                    </button>
                </p>
            </form>
        </div>
    );
}

export default Register;