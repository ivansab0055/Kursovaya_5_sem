import React, {useState, useEffect, useRef, useReducer} from "react";
import {Link} from "react-router-dom";
import './Navbar.css';

function NavBar() {
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('accessToken'));
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);
    const [_, forceUpdate] = useReducer(x => x + 1, 0);
    useEffect(() => {

        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [dropdownRef]);

    const handleDropdownItemClick = () => {
        setIsDropdownOpen(false);
    };

    return (
        <nav>
            <div className="logo-container">
                <Link to="/" style={{display: 'flex', alignItems: 'center', textDecoration: 'none'}}>
                    <img src={'/Kallosus_small.svg'} alt="Logo" style={{width: '50px', height: '50px', marginRight: '10px'}}/>
                    <span style={{
                        fontSize: '36px',
                        background: '#308A4C',
                        WebkitBackgroundClip: 'text',
                        color: 'transparent',
                        fontFamily: 'Aleo',
                        fontWeight: 'bold',
                        letterSpacing: '2px'
                    }}>
                KALLOSUS
                </span>
                </Link>
            </div>
            <ul>
                {isLoggedIn ? (
                    <li className="profile-icon-container">
                        <img
                            src={'/profile-icon.svg'}
                            alt="Profile"
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                        />
                        {isDropdownOpen && (
                            <ul className="dropdown-menu" ref={dropdownRef}>
                                <li><Link to="/LK" onClick={handleDropdownItemClick}>Личный кабинет</Link></li>
                                <li><Link to="/help" onClick={handleDropdownItemClick}>Помощь</Link></li>
                                <li><Link to="/settings" onClick={handleDropdownItemClick}>Настройки</Link></li> {/*В будущем Настройки*/}
                                <li><Link to="/logout" onClick={handleDropdownItemClick}>Выход</Link></li>
                            </ul>
                        )}
                    </li>
                ) : (
                    <li>
                        <Link to="/login" className="login-button">Вход</Link>
                    </li>
                )}
            </ul>
        </nav>
    );
}

export default NavBar;
