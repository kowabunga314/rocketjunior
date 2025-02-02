import React, { useState } from 'react';
import SearchInput from './SearchInput';
import TreeNode from './TreeNode';

const Tree = () => {
  const [treeData, setTreeData] = useState(null);

  const handleDelete = (nodeId) => { alert(`Deleted node ${nodeId}`) }
  const handleSetTreeData = (data) => { 
    if (data !== null) setTreeData(data);
  }

  // Set content for tree node
  let treeNode
  if (treeData !== null) {
    treeNode = <TreeNode key={treeData.id} node={treeData} depth={0} onDelete={handleDelete} />
  } else {
    treeNode = <span>Please enter a valid path in the input field</span>
  }

  return (
    <div className='mt-4 tree-container'>
      <div className='tree-search'>
        <SearchInput onResults={handleSetTreeData} />
      </div>
      <div className='tree-node-container'>
        {treeNode}
      </div>
    </div>
  );
};

export default Tree;
