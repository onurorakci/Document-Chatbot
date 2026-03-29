export default function UploadZone({ handleFileChange, isUploading }) {
  return (
    <div className="upload-zone">
      <h2>Upload a PDF or Image</h2>
      <p style={{ color: '#808495', marginBottom: '20px' }}>
        Select multiple files to combine them
      </p>
      <input type="file" multiple onChange={handleFileChange} />
      {isUploading && (
        <div className="processing-indicator">
          <p style={{ color: 'var(--st-red)', marginTop: '20px' }}>
            Processing Documents...
          </p>
        </div>
      )}
    </div>
  );
}
