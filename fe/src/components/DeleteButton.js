import ConfirmButton from './ConfirmButton';

const DeleteButton = ({ onDelete }) => {
  const handleDelete = () => { onDelete() }
  return <ConfirmButton
    messageText="Are you sure you want to delete this node?"
    buttonText="Delete"
    onConfirm={handleDelete}
    buttonType='btn-danger' />;
};

export default DeleteButton;
