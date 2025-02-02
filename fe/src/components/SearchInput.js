// src/SearchInput.js
import React, { useState, useEffect } from 'react';
import _ from 'lodash';
import { fetchTreeData } from '../services/apiService';
const SearchInput = ({ onResults }) => {
  const [query, setQuery] = useState('');
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
      onResults(data);
    } catch (error) {
      console.warn(error);
    }
  }, 300);

  useEffect(() => {
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query]);

  return (
    <input
      type="text"
      className={`form-control mb-3 border border-${requestStatus}`}
      placeholder="Enter node path (i.e. Rocket, Rocket/Stage1)"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
};

export default SearchInput;
