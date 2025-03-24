import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NoteBook from './pages/NoteBook';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/notebook/:id" element={<NoteBook />} />
      </Routes>
    </Router>
  );
}

export default App;