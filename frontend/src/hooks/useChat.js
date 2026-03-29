import { useState, useEffect, useRef } from 'react';
import { uploadFiles, sendChatMessage } from '../services/api';

const initialId = "default-chat";

export function useChat() {
  const [chats, setChats] = useState({
    [initialId]: {
      id: initialId,
      fileName: null,
      documentText: "",
      messages: []
    }
  });
  const [currentChatId, setCurrentChatId] = useState(initialId);
  const [userInput, setUserInput] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [errorModal, setErrorModal] = useState({ show: false, msg: "" });
  const [isBotThinking, setIsBotThinking] = useState(false);
  const messagesEndRef = useRef(null);

  const currentChat = chats[currentChatId];

  const scrollToLastMessage = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  };

  useEffect(() => {
    scrollToLastMessage();
  }, [currentChat?.messages, isBotThinking]);

  const createNewChat = () => {
    const newId = crypto.randomUUID();
    setChats(prev => ({
      ...prev,
      [newId]: { id: newId, fileName: null, documentText: "", messages: [] }
    }));
    setCurrentChatId(newId);
  };

  const handleFileChange = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length === 0) return;

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    const formData = new FormData();
    let fileNames = [];

    for (const file of selectedFiles) {
      if (!allowedTypes.includes(file.type)) {
        setErrorModal({ show: true, msg: `${file.name} is not an allowed file type.` });
        e.target.value = null;
        return;
      }
      formData.append('files', file);
      fileNames.push(file.name);
    }

    formData.append('chat_id', currentChatId);
    setIsUploading(true);

    try {
      await uploadFiles(formData);
      setChats(prev => ({
        ...prev,
        [currentChatId]: {
          ...prev[currentChatId],
          fileName: fileNames.join(", "),
          documentText: "loaded_on_backend"
        }
      }));
    } catch (error) {
      console.error("Upload error:", error);
      setErrorModal({ show: true, msg: "An error occurred while uploading files." });
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const sendMessage = async () => {
    if (!userInput.trim() || isBotThinking) return;

    const userMsg = { role: 'user', content: userInput };
    setChats(prev => ({
      ...prev,
      [currentChatId]: {
        ...prev[currentChatId],
        messages: [...prev[currentChatId].messages, userMsg]
      }
    }));

    const sentInput = userInput;
    setUserInput("");
    setIsBotThinking(true);

    const formData = new FormData();
    formData.append('chat_id', currentChatId);
    formData.append('message', sentInput);

    try {
      const data = await sendChatMessage(formData);
      const botMsg = { role: 'assistant', content: data.response };
      setChats(prev => ({
        ...prev,
        [currentChatId]: {
          ...prev[currentChatId],
          messages: [...prev[currentChatId].messages, botMsg]
        }
      }));
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsBotThinking(false);
    }
  };

  return {
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
  };
}
