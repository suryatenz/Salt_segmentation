import React, { useState } from 'react';
import './UploadForm.css';

function UploadForm() {
  const [file, setFile] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setResultImage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      // Expecting the backend to return a base64 string in the key 'result'
      setResultImage(`data:image/png;base64,${data.result.trim()}`);
    } catch (err) {
      setError('Error processing the image');
      console.error(err);
    }
  };

  return (
    <div className="upload-container">
      <h2 className="title">Seismic Salt Segmentation</h2>
      <div className="form-container">
        <form onSubmit={handleSubmit} className="upload-form">
          <input type="file" accept="image/*" onChange={handleChange} />
          <button type="submit">Upload & Process</button>
        </form>
      </div>
      {error && <p className="error-message">{error}</p>}
      {resultImage && (
        <div className="result-container">
          {/* <div className="result-box">
            <h4>Input Image</h4>
            <img
              src={URL.createObjectURL(file)}
              alt="Input"
            />
          </div> */}
          <div className="result-box">
            <h4>Predicted Mask</h4>
            <img
              src={resultImage}
              alt="Prediction"
            />
          </div>
        </div>
      )}
      <p className="note">
        Note: Ensure that the image uploaded is a seismic image.
      </p>
    </div>
  );
}

export default UploadForm;
