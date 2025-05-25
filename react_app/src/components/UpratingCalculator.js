import React, { useState } from 'react';
import axios from 'axios';
import InputParameters from './InputParameters';
import ResultsTable from './ResultsTable';

const UpratingCalculator = () => {
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

  return (
    <div className="app-container">
      <aside className="sidebar">
        <InputParameters
          value={value}
          setValue={setValue}
          startYear={startYear}
          setStartYear={setStartYear}
          selectedUprating={selectedUprating}
          setSelectedUprating={setSelectedUprating}
          upratingOptions={upratingOptions}
          setUpratingOptions={setUpratingOptions}
          roundingBase={roundingBase}
          setRoundingBase={setRoundingBase}
          roundingMethod={roundingMethod}
          setRoundingMethod={setRoundingMethod}
          onCalculate={calculateUprating}
          loading={loading}
        />
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
          <ResultsTable
            results={results}
            roundingMethod={roundingMethod}
            roundingBase={roundingBase}
          />
        )}
      </main>
    </div>
  );
};

export default UpratingCalculator; 