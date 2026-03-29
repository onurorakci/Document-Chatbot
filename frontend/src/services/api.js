export async function uploadFiles(formData) {
  const response = await fetch('http://localhost:8000/process-files', {
    method: 'POST',
    body: formData
  });
  if (!response.ok) throw new Error("File upload failed");
  return response;
}

export async function sendChatMessage(formData) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    body: formData
  });
  if (!response.ok) throw new Error("Chat request failed");
  return response.json();
}
