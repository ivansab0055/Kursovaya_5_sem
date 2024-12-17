// URL.js
export function URL_web() {
    return process.env.REACT_APP_URL_WEB;
}

export function URL_nn() {

    if (process.env.REACT_APP_REAL_PROD !== '1' || process.env.REACT_APP_NODE_ENV==='production')
        return process.env.REACT_APP_URL_NN;
    else return process.env.REACT_APP_URL_NN_TRUE_PROD;

}

