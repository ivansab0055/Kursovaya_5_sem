import axios from 'axios';
import {URL_web} from "./URL";

const validate_captcha = async (token) => {
    try {
        const response = await axios.post(URL_web() + 'services/validate_captcha', {
            token: token
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const subscription = async (access_token, status) => {
    try {
        const response = await axios.post(URL_web() + 'mailing/subscribe', {
            access_token: access_token,
            subscribe: status
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};
const login = async (email, password) => {
    try {
        const response = await axios.post(URL_web() + 'auth/login', {
            email,
            password
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const checkToken = async (reset_token) => {
    try {
        const response = await axios.post(URL_web() + 'token/check_token', {
            reset_token
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const resetPassword = async (reset_token, password) => {
    try {
        const response = await axios.post(URL_web() + 'auth/reset', {
            reset_token,
            password
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const signup = async (email, password, company) => {
    const env_confirmation_bool = process.env.REACT_APP_NODE_ENV === 'production'
    try {
        const response = await axios.post(URL_web() + 'auth/signup', {
            email,
            password,
            company,
            confirmation: env_confirmation_bool
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            if (!env_confirmation_bool) {
                console.log(response.data)
            }
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const confirmEmail = async (confirm_token) => {
    const env_emailing_bool = process.env.REACT_APP_NODE_ENV === 'production'
    try {
        const response = await axios.post(URL_web() + 'auth/confirm', {
            confirm_token,
            emailing: env_emailing_bool
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

//get user information
const confirmAccess = async (access_token) => {
    try {
        const response = await axios.get(URL_web() + 'auth/user', {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};


const changePassword = async (access_token, old_pass, new_pass) => {
    try {
        const env_emailing_bool = process.env.REACT_APP_NODE_ENV === 'production'
        const response = await axios.post(URL_web() + 'auth/change_password', {
            access_token: access_token,
            old_password: old_pass,
            new_password: new_pass,
            emailing: env_emailing_bool
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};


const refreshToken = async (refreshToken) => {
    try {
        const response = await axios.post(
            URL_web() + 'token/refresh',
            {},
            {
                headers: {
                    'Authorization': `Bearer ${refreshToken}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
        );

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};

const forgotPass = async (formData) => {
    const env_confirmation_bool = process.env.REACT_APP_NODE_ENV === 'production'
    try {
        const response = await axios.post(URL_web() + 'auth/forgot', {
            email: formData.email,
            confirmation: env_confirmation_bool

        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return response.data;
            // Handle successful response

        }
    } catch (error) {
        handleError(error);
        throw error;
    }
}

//////////////ADMIN QUERIES

const AdminUserUpdate = async (access_token, userID, updateData) => {
    try {
        const data = { access_token };
        if (updateData.email !== undefined) data.email = updateData.email;
        if (updateData.password !== undefined) data.password = updateData.password;
        if (updateData.role !== undefined) data.role = updateData.role;
        if (updateData.company !== undefined) data.company = updateData.company;
        const response = await axios.post(URL_web() + `admin/user/${userID}`, data, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });
        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};


const AdminUserDelete = async (access_token, userID) => {
    try {
        const response = await axios.delete(URL_web() + `admin/user/${userID}`, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};



const AdminLoginAsUser = async (access_token, userID) => {
    try {
        const response = await axios.get(URL_web() + `admin/login_as/${userID}`, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};


const AdminGetAllUsers = async (access_token) => {
    try {
        const response = await axios.get(URL_web() + 'admin/users', {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        handleError(error);
        throw error;
    }
};





const handleError = (error) => {
    if (error.response && process.env.REACT_APP_NODE_ENV === 'development') {
        switch (error.response.status) {
            case 500:
                console.error('InternalServerError');
                break;
            case 422:
                console.error('Decode Error');
                break;
            case 400:
                console.error('SomeRequestArgumentsMissing');
                break;
            case 401:
                console.error('Invalid username or password');
                break;
            case 403:
                console.error('Invalid token || ExpiredTokenError');
                break;
            default:
                console.error('Error:', error);
        }
    } else if (process.env.REACT_APP_NODE_ENV === 'development') {
        console.error('Error:', error);
    }
};
export {
    login,
    changePassword,
    subscription,
    checkToken,
    resetPassword,
    signup,
    confirmEmail,
    confirmAccess,
    refreshToken,
    forgotPass,
    validate_captcha,
    AdminUserUpdate,
    AdminUserDelete,
    AdminLoginAsUser,
    AdminGetAllUsers
};

