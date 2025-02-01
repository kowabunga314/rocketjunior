import React, { useState } from 'react';
import TreeNode from './TreeNode';

const Tree = ({ data }) => {
  return (
    <div className='container mt-4'>
      {data.map((node) => (
        <TreeNode key={node.id} node={node} depth={0} />
      ))}
    </div>
  );
};

export default Tree;
