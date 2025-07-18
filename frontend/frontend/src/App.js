import React, { useState, useRef, useEffect } from 'react';
import { FaFolderOpen, FaPaperPlane } from 'react-icons/fa';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatBoxRef = useRef(null);

  // Get or set sessionId from localStorage
  const getSessionId = () => {
    let sessionId = localStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = uuidv4();
      localStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
  };

  const sessionId = getSessionId();

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('session_id', sessionId); // include session ID

    const fileMessage = {
      sender: 'user',
      text: `<strong><span style="font-size: 18px;">📄 Uploaded:</span></strong> <i>${selectedFile.name}</i>`,
    };
    setMessages((prev) => [...prev, fileMessage]);

    try {
      const res = await fetch('http://192.168.56.55:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      const botResponse = {
        sender: 'bot',
        text: data.message || 'The uploaded document does not belong to our organization',
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: '❌ File upload failed. Try again.' },
      ]);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    const userMessage = { sender: 'user', text: question };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setQuestion('');

    try {
      const res = await fetch('http://192.168.56.55:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      });

      const data = await res.json();
      const botMessage = {
        sender: 'bot',
        text: data.answer || '🤖 No answer found.',
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: '❌ Failed to get an answer.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chatBoxRef.current?.scrollTo(0, chatBoxRef.current.scrollHeight);
  }, [messages]);

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h1 style={styles.title}>🤖 AllyBot</h1>
        <h2 style={styles.subheading}>
          Got a document or a question? <br /> Let's simplify it together.
        </h2>

        <div style={styles.chatBox} ref={chatBoxRef}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.message,
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                backgroundColor: msg.sender === 'user' ? '#DCF8C6' : '#E8EAF6',
              }}
            >
              <div>
                <strong>{msg.sender === 'user' ? 'You' : 'AllyBot'}:</strong>{' '}
                <span dangerouslySetInnerHTML={{ __html: msg.text }} />
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ ...styles.message, backgroundColor: '#E8EAF6' }}>
              <strong>AllyBot:</strong> Typing...
            </div>
          )}
        </div>

        <div style={styles.inputSection}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            style={styles.input}
            onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          />

          <button onClick={handleAsk} style={styles.sendButton}>
            <FaPaperPlane />
          </button>

          <label htmlFor="file-upload" style={styles.uploadIconButton}>
            <FaFolderOpen />
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    backgroundColor: '#f0f2f5',
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
  },
  card: {
    backgroundColor: '#ffffff',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '600px',
    display: 'flex',
    flexDirection: 'column',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '8px',
    textAlign: 'center',
    color: '#007acc',
  },
  subheading: {
    fontSize: '16px',
    color: '#555',
    marginBottom: '15px',
    textAlign: 'center',
    lineHeight: '1.5',
  },
  chatBox: {
    flex: 1,
    minHeight: '300px',
    maxHeight: '400px',
    overflowY: 'auto',
    padding: '10px',
    backgroundColor: '#f9f9f9',
    borderRadius: '10px',
    marginBottom: '15px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  message: {
    padding: '10px 15px',
    borderRadius: '10px',
    maxWidth: '80%',
    fontSize: '15px',
    lineHeight: '1.4',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  inputSection: {
    display: 'flex',
    gap: '10px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: '10px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    fontSize: '16px',
  },
  sendButton: {
    backgroundColor: '#007acc',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 15px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  uploadIconButton: {
    backgroundColor: 'green',
    color: '#fff',
    borderRadius: '50%',
    padding: '10px',
    cursor: 'pointer',
    fontSize: '18px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
};

export default App;
