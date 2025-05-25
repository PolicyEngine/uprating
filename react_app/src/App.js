import React from 'react';
import './App.css';
import UpratingCalculator from './components/UpratingCalculator';

const App = () => {
  return (
    <div className="app">
      <header className="app-header">
        <h1>PolicyEngine Uprating Calculator</h1>
      </header>
      <UpratingCalculator />
    </div>
  );
};

export default App;