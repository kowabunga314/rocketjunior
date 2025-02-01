import React, { useState } from 'react';
import PropTypes from 'prop-types'
import TreeNode from './TreeNode'

// TreeNode.PropTypes = {
//   node: PropTypes.object.isRequired,
//   level: PropTypes.number.isRequired
// }

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
