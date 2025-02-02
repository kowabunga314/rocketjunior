import React from 'react';
import Switch from 'react-switch';

const ThemeToggle = ({ isDark, toggleTheme }) => {
  return (
    <div className='theme-toggle d-flex flex-column'>
      <Switch 
        onChange={toggleTheme} 
        checked={isDark}
        onColor="#333333"
        onHandleColor="#000000"
        handleDiameter={30}
        uncheckedIcon={false}
        checkedIcon={false}
        boxShadow="0px 1px 5px rgba(0, 0, 0, 0.6)"
        activeBoxShadow="0px 0px 1px 10px rgba(100, 100, 100, 0.2)"
        height={20}
        width={48}
      />
      <label className='theme-toggle-label'>
        { isDark ? 'Dark' : 'Light' } Mode
      </label>
    </div>
  );
};

export default ThemeToggle;
