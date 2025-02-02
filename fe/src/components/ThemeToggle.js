import React from 'react';

const ThemeToggle = ({ isDark, toggleTheme }) => {
  return (
    <button className="btn btn-secondary mb-3 theme-toggle" onClick={toggleTheme}>
      {isDark ? "Switch to Light Mode" : "Switch to DarkMode" }
    </button>
  );
};

export default ThemeToggle;
