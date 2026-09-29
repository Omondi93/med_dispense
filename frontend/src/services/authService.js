```javascript
import API from "./api";

export const loginUser = async (email, password) => {
    const response = await API.post("/api/auth/login", {
        email,
        password,
    });

    return response.data;
};

export const registerUser = async (name, email, password) => {
    const response = await API.post("/api/auth/register", {
        name,
        email,
        password,
    });

    return response.data;
};
```
