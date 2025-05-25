import React from 'react';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const ResultsTable = ({ results, roundingMethod, roundingBase }) => {
  return (
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
  );
};

export default ResultsTable;
