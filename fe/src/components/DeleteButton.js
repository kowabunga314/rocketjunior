import ConfirmButton from './ConfirmButton';

const DeleteButton = ({ onDelete, name }) => {
  const handleDelete = () => { onDelete() }
  return <ConfirmButton
    messageText={`Are you sure you want to delete ${name}?`}
    buttonText="Delete"
    onConfirm={handleDelete}
    buttonType='btn-danger' />;
};

export default DeleteButton;
