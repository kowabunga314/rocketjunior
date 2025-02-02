
// Note: buttonType can use any value supported by bootstrap: https://getbootstrap.com/docs/4.1/components/buttons/
const ConfirmButton = ({ messageText, buttonText, onConfirm, buttonType=null }) => {
  const handleClick = () => {
    if (window.confirm(messageText)) {
      onConfirm();
    }
  };

  return (
    <button className={`btn btn-sm ms-2 ${buttonType === null ? 'btn-primary' : buttonType}`} onClick={handleClick}>
      {buttonText}
    </button>
  );
};

export default ConfirmButton;
