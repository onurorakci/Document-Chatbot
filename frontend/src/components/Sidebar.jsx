export default function Sidebar({ chats, currentChatId, setCurrentChatId, createNewChat }) {
  return (
    <div className="sidebar">
      <button onClick={createNewChat} className="new-chat-btn">
        ➕ New Chat
      </button>
      <div className="chat-list">
        {Object.values(chats).map(c => (
          <button
            key={c.id}
            onClick={() => setCurrentChatId(c.id)}
            className={`chat-item ${c.id === currentChatId ? 'active' : ''}`}
          >
            {c.fileName || "Empty Chat"}
          </button>
        ))}
      </div>
    </div>
  );
}
