import './App.css';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import React from 'react';

import Main from "./component/Main";
import Login from "./component/Login";
import PredictorPage from "./component/PredictorPage";
import Register from "./component/Register";
import Fixtures from "./component/Fixtures";
import Teams from "./component/Teams"


function App() {
  return (
      <Router>
        <Routes>
          <Route path="/" element={<Main />} />

          <Route path="/log" element={<Login/>} />

          <Route path="/pred" element={<PredictorPage/>} />

            <Route path="/register" element={<Register />} />
            <Route path="/f" element={<Fixtures />} />
            <Route path="/t" element={<Teams />} />




        </Routes>
      </Router>
  );
}

export default App;
