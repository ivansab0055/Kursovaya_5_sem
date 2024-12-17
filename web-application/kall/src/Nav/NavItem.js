import React from "react";
import { Link } from "react-router-dom";

function NavItem({ to, children, onClick }) {
    return (
        <Link to={to} onClick={onClick}>
            {children}
        </Link>
    );
}

export default NavItem;
