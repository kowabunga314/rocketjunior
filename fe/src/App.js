import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import ThemeToggle from './components/ThemeToggle';
import Tree from './components/Tree';

function App() {
  const [isDark, setIsDark] = useState(() => {
    const storedTheme = localStorage.getItem('theme');
    return storedTheme ? storedTheme === 'dark' : false;
  });
  useEffect(() => {
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [[isDark]]);

  const toggleDarkMode = () => setIsDark(!isDark);

  return (
    <div className={`App p-5 mh-100 ${ isDark ? 'dark-mode' : 'light-mode' }`}>
      <h1>Rocket Junior</h1>
      <ThemeToggle isDark={isDark} toggleTheme={toggleDarkMode} />
      <Tree />
    </div>
  );
}

export default App;
