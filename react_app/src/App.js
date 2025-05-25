import React from 'react';
import './styles/policyengine.css';
import UpratingCalculator from './components/UpratingCalculator';
import logo from './styles/logo.svg';

const App = () => {
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <img src={logo} alt="PolicyEngine Logo" className="logo" />
          <h1 className="title">Uprating Calculator</h1>
        </div>
      </header>
      <UpratingCalculator />
    </div>
  );
};

export default App;