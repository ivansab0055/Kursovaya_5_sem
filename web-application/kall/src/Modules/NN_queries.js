import axios from "axios";
import {URL_nn} from "./URL";


const get_status = async (storedAccessToken, currentTask_id) => {
    try {
        const response = await axios.post(URL_nn() + 'pd/v1.0.0/status', {
            access_token: storedAccessToken,
            task_id: currentTask_id
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { progress: response.data.progress, status: response.data.status, eta: response.data.eta };
        }
    } catch (error) {
        handleError(error);
    }
};

const predict = async (storedAccessToken, links_dict) => {
    try {
        const response = await axios.post(URL_nn() + 'pd/v1.0.0/predict', {
            access_token: storedAccessToken,
            queue_files: links_dict
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { task_id: response.data.task_id };
        }
    } catch (error) {
        handleError(error);
    }
};
const stop = async (storedAccessToken, currentTask_id) => {
    try {
        const response = await axios.post(URL_nn() + 'pd/v1.0.0/stop', {
            access_token: storedAccessToken,
            task_id: currentTask_id
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { message: response.message };
        }
    } catch (error) {
        handleError(error);
    }
};
const get_results = async (storedAccessToken) => {
    try {
        const response = await axios.post(URL_nn() + 'pd/v1.0.0/result', {
            access_token: storedAccessToken
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { files: response.data.files };
        }
    } catch (error) {
        handleError(error);
    }
};

const get_result = async (storedAccessToken, currentTask_id) => {
    try {
        const response = await axios.post(URL_nn() + 'pd/v1.0.0/result', {
            access_token: storedAccessToken,
            task_id: currentTask_id
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { files: response.data.files };
        }
    } catch (error) {
        handleError(error);
    }
};

const create_folders = async (storedAccessToken, number) => {
    try {
        const response = await axios.post(URL_nn() + 'file_management/v1.0.0/create', {
            access_token: storedAccessToken,
            num_folders: number
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });

        if (response.status === 200) {
            return { folders: response.data.folders };
        }
    } catch (error) {
        handleError(error);
    }
};

const handleError = (error) => {
    if (error.response && process.env.REACT_APP_NODE_ENV === 'development') {
        switch (error.response.status) {
            case 500:
                console.error('InternalServerError');
                break;
            case 401:
                console.error('ExpiredTokenError')
                break
            case 404:
                console.error('ExistionError')
                break
            case 400:
                console.error('SomeRequestArgumentsMissing');
                break;
            default:
                console.error('Error:', error);
        }
    }  else if(process.env.REACT_APP_NODE_ENV === 'development') {
        console.error('Error:', error);
    }
    throw error;
};

export { get_status, predict, get_results, get_result, create_folders, stop };