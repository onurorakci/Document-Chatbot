export default function ErrorModal({ errorModal, setErrorModal }) {
  if (!errorModal.show) return null;

  return (
    <div className="custom-modal-overlay">
      <div className="custom-modal">
        <div className="modal-header">Loading Error</div>
        <div className="modal-body">{errorModal.msg}</div>
        <button
          className="modal-btn"
          onClick={() => setErrorModal({ show: false, msg: "" })}
        >
          OK
        </button>
      </div>
    </div>
  );
}
