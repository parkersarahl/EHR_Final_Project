import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const PatientDetails = () => {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [error, setError] = useState('');
  const [labs, setLabs] = useState([]);
  const [notes, setNotes] = useState([]);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setError('');
        const res = await axios.get(`/api/epic/patients/${id}`);
        setPatient(res.data.patient);
        setLabs(res.data.labs);
        setNotes(res.data.notes);
      } catch (err) {
        setError('Failed to load patient details');
      }
    };
    fetchDetails();
  }, [id]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!patient) return <p>Loading...</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">{patient.name}</h2>
      <p><strong>DOB:</strong> {patient.birthDate}</p>

      <h3 className="mt-6 text-lg font-semibold">Lab Results</h3>
      <ul className="list-disc ml-5">
        {labs.map((lab, index) => (
          <li key={index}>{lab}</li>
        ))}
      </ul>

      <h3 className="mt-6 text-lg font-semibold">Clinical Notes</h3>
      <ul className="list-disc ml-5">
        {notes.map((note, index) => (
          <li key={index}>{note}</li>
        ))}
      </ul>
    </div>
  );
};

export default PatientDetails;
