import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PatientSearch from './PatientSearch';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 p-4">
        <nav className="mb-6 space-x-4">
          <Link to="/" className="text-blue-600 hover:underline">Home</Link>
          <Link to="/search-patients" className="text-blue-600 hover:underline">Search Patients</Link>
        </nav>

        <Routes>
          <Route path="/" element={<div className="text-lg">Welcome to the Patient App</div>} />
          <Route path="/search-patients" element={<PatientSearch />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
// Compare this snippet from Final%20Project/frontend/src/SearchPatients.js:
