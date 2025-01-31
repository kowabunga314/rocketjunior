// src/App.js
import React from 'react';
import './App.css';
import Tree from './Tree';

// Example data
const sampleData = [
  {
    id: 1,
    name: 'Rocket',
    properties: { Mass: '12000.000', Height: '18.000' },
    descendants: [
      {
        id: 2,
        name: 'Stage1',
        properties: {},
        descendants: [
          {
            id: 4,
            name: 'Engine1',
            properties: { ISP: '12.156', Thrust: '9.493' },
            descendants: []
          },
          {
            id: 5,
            name: 'Engine2',
            properties: { ISP: '11.632', Thrust: '9.413' },
            descendants: []
          }
        ]
      }
    ]
  }
];

function App() {
  return (
    <div className="App">
      <h1>Tree Visualization WUMBO</h1>
      <Tree data={sampleData} />
    </div>
  );
}

export default App;
