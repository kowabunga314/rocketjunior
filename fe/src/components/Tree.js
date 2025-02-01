import React, { useState } from 'react';
import TreeNode from './TreeNode';

const Tree = ({ data }) => {
  const handleDelete = (nodeId) => {
    alert(`Deleted node ${nodeId}`)
  }
  return (
    <div className='container mt-4'>
      {data.map((node) => (
        <TreeNode key={node.id} node={node} depth={0} onDelete={handleDelete} />
      ))}
    </div>
  );
};

export default Tree;
