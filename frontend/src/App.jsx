import './App.css';
import { useChat } from './hooks/useChat';
import ErrorModal from './components/ErrorModal';
import Sidebar from './components/Sidebar';
import UploadZone from './components/UploadZone';
import MessageList from './components/MessageList';
import InputBox from './components/InputBox';

function App() {
  const {
    chats,
    currentChatId,
    setCurrentChatId,
    currentChat,
    userInput,
    setUserInput,
    isUploading,
    isBotThinking,
    errorModal,
    setErrorModal,
    messagesEndRef,
    createNewChat,
    handleFileChange,
    sendMessage
  } = useChat();

  return (
    <div className="app-wrapper">
      <ErrorModal errorModal={errorModal} setErrorModal={setErrorModal} />

      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        setCurrentChatId={setCurrentChatId}
        createNewChat={createNewChat}
      />

      <div className="main">
        <header className="app-header">
          <h1>💬 DOCUMENT CHATBOT</h1>
        </header>

        <div className="messages-area">
          {currentChat && !currentChat.documentText && currentChat.messages.length === 0 && (
            <UploadZone handleFileChange={handleFileChange} isUploading={isUploading} />
          )}

          <MessageList
            currentChat={currentChat}
            isBotThinking={isBotThinking}
            messagesEndRef={messagesEndRef}
          />
        </div>

        {currentChat?.fileName && (
          <InputBox
            userInput={userInput}
            setUserInput={setUserInput}
            sendMessage={sendMessage}
          />
        )}
      </div>
    </div>
  );
}

export default App;
