import React, { useState } from 'react';

const showOriginalTimestamp = false;

const TimeSince = ({ timestamp }) => {
  const [showOriginalTimestamp, setShowOriginalTimestamp] = useState(false)
  const localeString = showOriginalTimestamp ? ` (${new Date(timestamp).toLocaleString()})` : ''
  const toggleShowOriginalTimestamp = () => setShowOriginalTimestamp(!showOriginalTimestamp)

  return (
    <div
      className='pl-4 d-flex justify-content-start font-weight-light text-muted'
      style={{ cursor: 'pointer' }}
      onClick={toggleShowOriginalTimestamp}
    >
      Created {getTimeSince(timestamp)}{localeString}
    </div>
  )
};

const getTimeSince = (createdAt) => {
  const createdDate = new Date(createdAt);
  const now = new Date();
  // Get timedelta between createdAt and now
  const diffInSeconds = Math.floor((now - createdDate) / 1000);

  if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`;
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours} hours ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 365) return `${diffInDays} days ago`;
  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} years ago`;
};

export default TimeSince;
