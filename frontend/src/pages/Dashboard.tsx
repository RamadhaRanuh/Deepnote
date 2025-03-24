import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/pages/Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [notebooks, setNotebooks] = useState([
    {
      id: '1',
      title: 'Research Paper Notes',
      lastModified: 'Modified Mar 20, 2025',
      description: 'Notes on AI research papers'
    },
    {
      id: '2',
      title: 'Project Documentation',
      lastModified: 'Modified Mar 18, 2025',
      description: 'PDF Retrieval System documentation'
    },
    {
      id: '3',
      title: 'Learning Resources',
      lastModified: 'Modified Mar 15, 2025',
      description: 'ML/AI learning materials'
    }
  ]);

  const navigateToNotebook = (notebookId = 'new') => {
    navigate(`/notebook/${notebookId}`);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>DeepNotebook</h1>
        </div>
        <div className="header-right">
          <button className="settings-button">
            <span className="material-icon">settings</span>
          </button>
          <div className="user-profile">
            <div className="avatar">UR</div>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        <h1>
          Welcome to DeepNotebook
        </h1>
        <div className="notebooks-header">
          <h2>Your notebooks</h2>
        </div>
        
        <div className="notebooks-grid">
          {/* Create new notebook card */}
          <div className="notebook-card create-new" onClick={() => navigateToNotebook()}>
            <div className="create-icon">+</div>
            <p>Create new</p>
          </div>
          
          {/* Existing notebooks */}
          {notebooks.map(notebook => (
            <div 
              key={notebook.id} 
              className="notebook-card"
              onClick={() => navigateToNotebook(notebook.id)}
            >
              <div className="notebook-content">
                <h3>{notebook.title}</h3>
                <p className="notebook-description">{notebook.description}</p>
              </div>
              <div className="notebook-footer">
                <span className="last-modified">{notebook.lastModified}</span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;