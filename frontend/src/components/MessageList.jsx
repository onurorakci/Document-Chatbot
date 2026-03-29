import ReactMarkdown from 'react-markdown';

export default function MessageList({ currentChat, isBotThinking, messagesEndRef }) {
  return (
    <>
      {currentChat?.messages.map((m, i) => {
        const isLastMessage = i === currentChat.messages.length - 1;
        return (
          <div
            key={i}
            ref={isLastMessage && !isBotThinking ? messagesEndRef : null}
            className={`msg ${m.role}`}
          >
            <ReactMarkdown>{m.content}</ReactMarkdown>
          </div>
        );
      })}

      {isBotThinking && (
        <div ref={messagesEndRef} className="msg assistant loading">
          <div className="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      )}
    </>
  );
}
