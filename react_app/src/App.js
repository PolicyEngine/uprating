import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  // State for input parameters
  const [value, setValue] = useState(1000);
  const [startYear, setStartYear] = useState(2024);
  const [projectionYears] = useState(20);
  const [selectedUprating, setSelectedUprating] = useState('gov.irs.uprating');
  const [upratingOptions, setUpratingOptions] = useState([]);
  const [roundingBase, setRoundingBase] = useState(1);
  const [roundingMethod, setRoundingMethod] = useState('nearest');
  
  // State for results
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);

  // Fetch uprating options on component mount
  useEffect(() => {
    fetchUpratingOptions();
  }, []);

  const fetchUpratingOptions = async () => {
    try {
      const response = await axios.get('/api/uprating-options');
      setUpratingOptions(response.data);
    } catch (err) {
      console.error('Error fetching uprating options:', err);
      setError('Failed to fetch uprating options. Please make sure the backend server is running on port 8000.');
    }
  };

  const calculateUprating = async () => {
    setLoading(true);
    setError(null);
    setWarnings([]);
    
    try {
      const response = await axios.post('/api/calculate', {
        value,
        startYear,
        projectionYears,
        selectedUprating,
        roundingBase,
        roundingMethod,
      });
      
      setResults(response.data.results);
      setWarnings(response.data.warnings || []);
    } catch (err) {
      console.error('Error calculating uprating:', err);
      setError(err.response?.data?.error || 'Failed to calculate uprating. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const formatPercentage = (num) => {
    return `${(num * 100).toFixed(2)}%`;
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>PolicyEngine Uprating Calculator</h1>
      </header>
      
      <div className="app-container">
        <aside className="sidebar">
          <h2>Input Parameters</h2>
          
          <div className="input-group">
            <label htmlFor="value">Enter value to be uprated:</label>
            <input
              id="value"
              type="number"
              min="0"
              step="100"
              value={value}
              onChange={(e) => setValue(parseFloat(e.target.value) || 0)}
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="startYear">Enter start year:</label>
            <input
              id="startYear"
              type="number"
              min="2015"
              max="2035"
              step="1"
              value={startYear}
              onChange={(e) => setStartYear(parseInt(e.target.value) || 2024)}
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="uprating">Select uprating parameter:</label>
            <select
              id="uprating"
              value={selectedUprating}
              onChange={(e) => setSelectedUprating(e.target.value)}
            >
              {upratingOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <h3>Rounding Options</h3>
          
          <div className="input-group">
            <label htmlFor="roundingBase">Round to:</label>
            <input
              id="roundingBase"
              type="number"
              min="0.01"
              max="10000"
              step="0.01"
              value={roundingBase}
              onChange={(e) => setRoundingBase(parseFloat(e.target.value) || 1)}
            />
          </div>
          
          <div className="input-group">
            <label>Rounding method:</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  value="nearest"
                  checked={roundingMethod === 'nearest'}
                  onChange={(e) => setRoundingMethod(e.target.value)}
                />
                Round nearest
              </label>
              <label>
                <input
                  type="radio"
                  value="upwards"
                  checked={roundingMethod === 'upwards'}
                  onChange={(e) => setRoundingMethod(e.target.value)}
                />
                Round upwards
              </label>
              <label>
                <input
                  type="radio"
                  value="downwards"
                  checked={roundingMethod === 'downwards'}
                  onChange={(e) => setRoundingMethod(e.target.value)}
                />
                Round downwards
              </label>
            </div>
          </div>
          
          <button 
            className="calculate-button"
            onClick={calculateUprating}
            disabled={loading}
          >
            {loading ? 'Calculating...' : 'Calculate Uprated Values'}
          </button>
        </aside>
        
        <main className="main-content">
          {error && (
            <div className="error-message">
              Error: {error}
            </div>
          )}
          
          {warnings.length > 0 && (
            <div className="warnings">
              {warnings.map((warning, index) => (
                <div key={index} className="warning-message">
                  {warning}
                </div>
              ))}
            </div>
          )}
          
          {results && (
            <div className="results">
              <h2>Uprated Values (with Rounding)</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Uprating Factor</th>
                      <th>Pre-Rounded Value</th>
                      <th>Rounded Value ({roundingMethod} to {roundingBase})</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, index) => (
                      <tr key={index}>
                        <td>{row.year}</td>
                        <td>{row.upratingFactor === 0 ? 'N/A' : formatPercentage(row.upratingFactor)}</td>
                        <td>{formatCurrency(row.originalValue)}</td>
                        <td>{formatCurrency(row.roundedValue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;