// src/SearchInput.js
import React, { useState, useEffect } from 'react';
import _ from 'lodash';
import { fetchTreeData } from '../services/apiService';
const SearchInput = ({ onResults }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requestStatus, setRequestStatus] = useState('warning');

  // Debounced function that calls the API service
  const debouncedSearch = _.debounce(async (searchTerm) => {
    try {
      const data = await fetchTreeData(searchTerm || "");
      if (data !== null) {
        setRequestStatus('info');
      } else {
        setRequestStatus('warning');
      }
      setIsLoading(false);
      onResults(data);
    } catch (error) {
      console.warn(error);
    }
  }, 300);

  useEffect(() => {
    setIsLoading(true);
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query]);

  return (
    <div className='input-group mb3'>
      <input
        type="text"
        placeholder="Enter node path (i.e. Rocket, Rocket/Stage1)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ paddingRight: '40px' }}
        className={`form-control mb-3 border border-${requestStatus}`}
      />
      {isLoading && (
        <div 
          style={{
            position: 'absolute',
            right: '20px',
            top: '8px',
            zIndex: '1000'
          }}
        >
          <span
            className="spinner-border spinner-border-sm"
            role="status"
            aria-hidden="true"
          ></span>
        </div>
      )}
    </div>
  );
};

export default SearchInput;
