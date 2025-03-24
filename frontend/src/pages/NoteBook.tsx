import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../../styles/pages/Notebook.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
}

function NoteBook() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [notebookTitle, setNotebookTitle] = useState(id === 'new' ? 'New Notebook' : '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Simulate loading notebook data
  useEffect(() => {
    if (id === 'new') {
      setIsLoading(false);
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: 'Welcome to your new notebook! Upload PDFs and ask questions about them.',
          timestamp: new Date()
        }
      ]);
      return;
    }

    // Simulate fetching existing notebook data
    setTimeout(() => {
      // This would be replaced with actual API calls
      setNotebookTitle(`Notebook ${id}`);
      setDocuments([
        { id: '1', name: 'Sample Document.pdf', size: 2500000, type: 'application/pdf' }
      ]);
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Welcome back to Notebook ${id}! How can I help you today?`,
          timestamp: new Date()
        }
      ]);
      setIsLoading(false);
    }, 800);
  }, [id]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsSendingMessage(true);
    
    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `This is a simulated response to: "${inputMessage}". In a real implementation, this would use the DeepSeek model to analyze your documents and generate a relevant response.`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setIsSendingMessage(false);
    }, 1500);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Process uploaded files
    const newDocs: Document[] = Array.from(files).map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
      name: file.name,
      size: file.size,
      type: file.type
    }));

    setDocuments(prev => [...prev, ...newDocs]);
    
    // Add system message about upload
    const fileNames = newDocs.map(doc => doc.name).join(', ');
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Uploaded ${newDocs.length} document(s): ${fileNames}`,
        timestamp: new Date()
      }
    ]);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNotebookTitle(e.target.value);
  };

  const goBack = () => {
    navigate('/');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (isLoading) {
    return (
      <div className="notebook-loading">
        <div className="loading-spinner"></div>
        <p>Loading notebook...</p>
      </div>
    );
  }

  return (
    <div className="notebook-container">
      <div className="notebook-sidebar">
        <div className="sidebar-header">
          <button className="back-button" onClick={goBack}>
            <span className="material-icon">arrow_back</span>
          </button>
          <h2>DeepNotebook</h2>
        </div>
        
        <div className="sidebar-content">
          <div className="sidebar-section">
            <h3>Documents</h3>
            <div className="documents-list">
              {documents.length === 0 ? (
                <p className="empty-state">No documents uploaded yet</p>
              ) : (
                documents.map(doc => (
                  <div className="document-item" key={doc.id}>
                    <div className="document-icon">
                      <span className="material-icon">description</span>
                    </div>
                    <div className="document-details">
                      <span className="document-name">{doc.name}</span>
                      <span className="document-size">{formatFileSize(doc.size)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
        
        <div className="sidebar-footer">
          <input
            type="file"
            ref={fileInputRef}
            id="file-upload"
            multiple
            accept=".pdf"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-upload" className="upload-button">
            <span className="material-icon">upload_file</span>
            Upload PDF
          </label>
        </div>
      </div>
      
      <div className="notebook-main">
        <div className="notebook-header">
          <input
            type="text"
            className="notebook-title-input"
            value={notebookTitle}
            onChange={handleTitleChange}
            placeholder="Enter notebook title..."
          />
        </div>
        
        <div className="chat-container">
          <div className="messages-container">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? 'UR' : 'AI'}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-timestamp">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            
            {isSendingMessage && (
              <div className="message assistant-message">
                <div className="message-avatar">AI</div>
                <div className="message-content">
                  <div className="thinking-dots">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <div className="message-input-container">
            <textarea
              className="message-input"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask a question about your documents..."
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={isSendingMessage}
            />
            <button 
              className="send-button" 
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isSendingMessage}
            >
              <span className="material-icon">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NoteBook;