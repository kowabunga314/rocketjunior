import React, { useState } from 'react';

const Property = ({ propKey, propValue }) => {
  return (
    <div className='mb-1 d-flex justify-content-start' style={{ gap: '0.5rem' }}>
      <strong>{propKey}: </strong>{' '}
      <span style={{ color: propValue > 10 ? 'green' : '' }}> {propValue}</span>
    </div>
  )
}

export default Property;
