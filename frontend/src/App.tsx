import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NoteBook from './pages/NoteBook';
import { ThemeProvider } from './components/settings/ThemeProvider';
import './App.css';
import '../styles/global.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/notebook/:id" element={<NoteBook />} />
        </Routes>
      </Router>
    </ThemeProvider>
    
  );
}

export default App;