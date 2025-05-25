import React, { useEffect } from 'react';
import axios from 'axios';

const InputParameters = ({
  value,
  setValue,
  startYear,
  setStartYear,
  selectedUprating,
  setSelectedUprating,
  upratingOptions,
  setUpratingOptions,
  roundingBase,
  setRoundingBase,
  roundingMethod,
  setRoundingMethod,
  onCalculate,
  loading
}) => {
  useEffect(() => {
    fetchUpratingOptions();
  }, []);

  const fetchUpratingOptions = async () => {
    try {
      const response = await axios.get('/api/uprating-options');
      setUpratingOptions(response.data);
    } catch (err) {
      console.error('Error fetching uprating options:', err);
    }
  };

  return (
    <>
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
        onClick={onCalculate}
        disabled={loading}
      >
        {loading ? 'Calculating...' : 'Calculate Uprated Values'}
      </button>
    </>
  );
};

export default InputParameters; 