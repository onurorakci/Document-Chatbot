export default function InputBox({ userInput, setUserInput, sendMessage }) {
  return (
    <div className="input-container">
      <div className="input-box">
        <input
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a question..."
        />
        <button onClick={sendMessage} className="send-btn">Send</button>
      </div>
    </div>
  );
}
