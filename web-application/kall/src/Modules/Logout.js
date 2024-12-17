import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

function Logout() {
    const navigate = useNavigate();
    useEffect(() => {


        localStorage.clear()
        //window.location.reload();
        window.location.href = '/'
    }, [navigate]);



}

export default Logout