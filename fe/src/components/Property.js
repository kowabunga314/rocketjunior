import React, { useState } from 'react';

const Property = ({ propKey, propValue }) => {
  return (
    <div className='mb-1 border border-info d-flex justify-content-start'>
      <strong>{propKey}: </strong>
      <span style={{ color: propValue > 10 ? 'green' : 'black' }}>{propValue}</span>
    </div>
  )
}

export default Property;
