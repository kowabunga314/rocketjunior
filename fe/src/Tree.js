// src/Tree.js
import React, { useState } from 'react';

const TreeNode = ({ node, depth }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed)
  }
  return (
    <div style={{ marginLeft: depth * 20 + 'px' }}>
      <div onClick={toggleCollapse} style={{ cursor: 'pointer', fontWeight: 'bold' }}>
        {isCollapsed ? '▶' : '▼'} {node.name}
      </div>

      {/* Render properties if any */}
      {Object.entries(node.properties).map(([key, value]) => (
        <div key={key}>
          {key}: {value > 10 ? <span style={{ color: 'green' }}>{value}</span> : value}
        </div>
      ))}

      {/* Render descendants */}
      {!isCollapsed && node.descendants && node.descendants.length > 0 && (
        <div>
          {node.descendants.map((childNode) => (
            <TreeNode key={childNode.id} node={childNode} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

const Tree = ({ data }) => {
  return (
    <div>
      {data.map((node) => (
        <TreeNode key={node.id} node={node} depth={0} />
      ))}
    </div>
  );
};

export default Tree;
