import React from 'react';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';

import Home from './Pages/Home';
import Login from './Pages/Login';
import Logout from './Modules/Logout';
import Signup from './Pages/Signup';
import Navbar from './Nav/Navbar';
import Settings from './Pages/Settings';
import Help from './Pages/Help';
import EmailConfirm from './Pages/Email_conformation';
import LK from './Pages/LK';
import GoToConfirm from './Pages/GoToConfirm';
import ForgotPassword from './Pages/ForgotPassword';
import ResetPassword from './Pages/ResetPassword';
import Documents from './Pages/Documents';
import NotFoundPage from "./Pages/NotFoundPage";
import Preloader from "./Modules/Preloader";
import AdminLK from "./Pages/AdminLK";

function App() {
    return (

        <Router>
            <div>
                <Preloader />
                <Navbar/>
                <Routes>
                    <Route path="/" element={<Home/>}/>
                    <Route path="/settings" element={<Settings/>}/>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/logout" element={<Logout/>}/>
                    <Route path="/help" element={<Help/>}/>
                    <Route path="/forgot" element={<ForgotPassword/>}/>
                    <Route path="/signup" element={<Signup/>}/>
                    <Route path="/go_to_confirm" element={<GoToConfirm/>}/>
                    <Route path="/confirm"/>
                    <Route path="/lk" element={<LK/>}/>
                    <Route path="/adminlk" element={<AdminLK/>}/>
                    <Route exact path="/confirm/:token" element={<EmailConfirm/>}/>
                    <Route exact path="/reset/:token" element={<ResetPassword/>}/>
                    <Route path="/documents" element={<Documents/>} />
                    <Route path="*" element={<NotFoundPage/>} />
                </Routes>

            </div>
        </Router>
    );
}

export default App;