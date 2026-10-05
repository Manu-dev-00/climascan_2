import { useState, useCallback } from 'react';
import { Upload, FileSpreadsheet, Download, Loader2, X, Cloud } from 'lucide-react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

function App() {
  const [stationName, setStationName] = useState('');
  const [stationCode, setStationCode] = useState('');
  const [observationMonth, setObservationMonth] = useState('2025-04');

  const [files, setFiles] = useState([]);
  const [preview, setPreview] = useState([]);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': [] }
  });

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleProcess = async () => {
    if (!stationName.trim()) return alert("Nom de station requis");
    if (files.length === 0) return alert("Ajoutez au moins une image");

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('station_name', stationName.trim());
    if (stationCode) formData.append('station_code', stationCode.trim());
    formData.append('observation_month', observationMonth);

    files.forEach(file => formData.append('files', file));

    try {
      const res = await axios.post('http://localhost:8000/api/process-station', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setJobId(res.data.job_id);
      setPreview(res.data.preview || []);
      setMessage(res.data.message);
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur de traitement");
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (type) => {
    if (!jobId) return;
    window.open(`http://localhost:8000/api/download/${jobId}/${type}`, '_blank');
  };

  const reset = () => {
    setFiles([]);
    setPreview([]);
    setJobId(null);
    setMessage('');
    setStationName('');
    setStationCode('');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex justify-center items-center gap-3 mb-8">
          <Cloud size={48} className="text-blue-600" />
          <h1 className="text-5xl font-bold text-gray-800">CliMaScan</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Infos Station */}
          <div className="lg:col-span-5 bg-white rounded-3xl shadow p-8">
            <h2 className="text-2xl font-semibold mb-6">Station</h2>
            <div className="space-y-6">
              <input
                type="text"
                placeholder="Nom de la Station *"
                value={stationName}
                onChange={(e) => setStationName(e.target.value)}
                className="w-full px-4 py-3 border rounded-2xl"
              />
              <input
                type="text"
                placeholder="Code Station (optionnel)"
                value={stationCode}
                onChange={(e) => setStationCode(e.target.value)}
                className="w-full px-4 py-3 border rounded-2xl"
              />
              <input
                type="month"
                value={observationMonth}
                onChange={(e) => setObservationMonth(e.target.value)}
                className="w-full px-4 py-3 border rounded-2xl"
              />
            </div>

            <button
              onClick={handleProcess}
              disabled={loading || !stationName || files.length === 0}
              className="mt-10 w-full bg-blue-600 text-white py-4 rounded-2xl font-semibold flex items-center justify-center gap-3 disabled:bg-gray-400"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Upload />}
              {loading ? "Traitement en cours..." : "Lancer OCR"}
            </button>
          </div>

          {/* Upload Zone */}
          <div className="lg:col-span-7">
            <div {...getRootProps()} className={`border-2 border-dashed rounded-3xl p-20 text-center cursor-pointer ${isDragActive ? 'border-blue-600 bg-blue-50' : 'border-gray-300'}`}>
              <input {...getInputProps()} />
              <Upload size={60} className="mx-auto text-gray-400 mb-4" />
              <p className="text-xl">Déposez les images de la station</p>
            </div>

            {files.length > 0 && (
              <div className="mt-6 space-y-2">
                {files.map((file, i) => (
                  <div key={i} className="flex justify-between items-center bg-white p-4 rounded-2xl border">
                    <span>{file.name}</span>
                    <button onClick={() => removeFile(i)} className="text-red-500">
                      <X />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {error && <p className="text-red-600 mt-6">{error}</p>}
        {message && (
          <div className="mt-10 bg-green-50 p-8 rounded-3xl">
            <h3 className="text-xl font-bold mb-4">✅ {message}</h3>
            <div className="flex gap-4">
              <button onClick={() => downloadFile('excel')} className="bg-indigo-600 text-white px-6 py-3 rounded-xl">Télécharger Excel</button>
              <button onClick={() => downloadFile('csv')} className="bg-emerald-600 text-white px-6 py-3 rounded-xl">Télécharger CSV</button>
              <button onClick={reset} className="border px-6 py-3 rounded-xl">Nouvelle Station</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;