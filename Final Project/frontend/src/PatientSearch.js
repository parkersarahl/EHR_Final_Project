import React, { useState } from 'react';
import axios from 'axios';

const PatientSearch = () => {
  const [familyName, setFamilyName] = useState('');
  const [givenName, setGivenName] = useState('');
  const [birthdate, setBirthdate] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    try {
      setError('');
      const params = new URLSearchParams();
      if (familyName) params.append('family_name', familyName);
      if (givenName) params.append('given_name', givenName);
      if (birthdate) params.append('birthdate', birthdate);

      const response = await axios.get(`/api/epic/patients?${params.toString()}`);
      setResults(response.data.results || []);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Search failed');
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">Search Patients</h2>
      <div className="space-y-2">
        <input
          type="text"
          placeholder="Family Name"
          value={familyName}
          onChange={(e) => setFamilyName(e.target.value)}
          className="border p-2 w-full"
        />
        <input
          type="text"
          placeholder="Given Name"
          value={givenName}
          onChange={(e) => setGivenName(e.target.value)}
          className="border p-2 w-full"
        />
        <input
          type="date"
          placeholder="Birthdate"
          value={birthdate}
          onChange={(e) => setBirthdate(e.target.value)}
          className="border p-2 w-full"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      <ul className="mt-6 space-y-2">
        {results.map((patient, index) => (
          <li key={index} className="border p-2 rounded shadow">
            <strong>{patient.name}</strong> (DOB: {patient.birthDate})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PatientSearch;
