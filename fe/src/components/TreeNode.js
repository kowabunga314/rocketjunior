import React, { useState } from 'react';
import PropTypes from 'prop-types'

import DeleteButton from './DeleteButton';
import Property from './Property'
import TimeSince from './TimeSince'

// Set depth after which we automatically collapse nodes
const autoCollapseDepth = 5;

const TreeNode = ({ node, depth, onDelete }) => {
  const [isCollapsed, setIsCollapsed] = useState(depth >= autoCollapseDepth);

  const toggleCollapse = () => { setIsCollapsed(!isCollapsed); }

  return (
    <div style={{ marginLeft: depth * 20 + 'px' }} className="mb-2 pt-2 border-top">
      <div 
        onClick={toggleCollapse}
        style={{ cursor: 'pointer', fontWeight: 'bold' }}
        className='d-flex justify-content-start align-items-center font-weight-bold'
      >
        <h5>{isCollapsed ? '▶' : '▼'} {node.name}</h5>
      </div>

      {!isCollapsed && <div className='mb-3 pb-2 important-indent'>
        {/* Render time since created and delete button in same row */}
        <div className='p-2 d-flex flex-row justify-content-between'>
          <TimeSince timestamp={node.created_at} />
          <DeleteButton onDelete={() => onDelete(node.id) } name={node.name} />
        </div>

        {/* Render properties if any */}
        {Object.keys(node.properties).length > 0 && <div className='p-2'>
          {Object.entries(node.properties).map(([key, value]) => (
            <Property key={key} propKey={key} propValue={value} />
          ))}
        </div>}
      </div>}

      {/* Render descendants */}
      {!isCollapsed && node.descendants && node.descendants.length > 0 && (
        <div>
          {node.descendants.map((descendant) => (
            <TreeNode key={descendant.id} node={descendant} depth={depth + 1} onDelete={() => onDelete(descendant.id)} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;