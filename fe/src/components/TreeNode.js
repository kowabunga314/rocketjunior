import React, { useState } from 'react';
import PropTypes from 'prop-types'
import Property from './Property'
import TimeSince from './TimeSince'

const TreeNode = ({ node, depth }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => { setIsCollapsed(!isCollapsed); }

  return (
    <div style={{ marginLeft: depth * 20 + 'px' }} className="mb-2 border-top">
      <div 
        onClick={toggleCollapse}
        style={{ cursor: 'pointer', fontWeight: 'bold' }}
        className='d-flex justify-content-start align-items-center font-weight-bold'
      >
        {isCollapsed ? '▶' : '▼'} {node.name}
      </div>


      <div className='ml-4 p-2'>
        <TimeSince timestamp={node.created_at} />
      </div>

      {/* Render properties if any */}
      <div className='ml-4 p-2'>
        {Object.entries(node.properties).map(([key, value]) => (
          <Property key={key} propKey={key} propValue={value} />
        ))}
      </div>

      {/* Render descendants */}
      {!isCollapsed && node.descendants && node.descendants.length > 0 && (
        <div>
          {node.descendants.map((descendant) => (
            <TreeNode key={descendant.id} node={descendant} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;