import axios from "axios";

const API = axios.create({

    baseURL:
    "http://127.0.0.1:5000/api"

});


// Automatically attach JWT token

API.interceptors.request.use(

    (config) => {

        const token =
        localStorage.getItem(
            "token"
        );

        if (token) {

            config.headers.Authorization =
            `Bearer ${token}`;

        }

        return config;

    },

    (error) => {

        return Promise.reject(
            error
        );

    }

);

export default API;