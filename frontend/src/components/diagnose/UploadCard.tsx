import React, { useRef, useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';

interface UploadCardProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({ selectedFile, onFileSelect }) => {
  const { t } = useI18n();
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      showToast('Please upload a valid image file (JPG or PNG).', 'error');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showToast('Image file must be under 10 MB.', 'error');
      return;
    }

    onFileSelect(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="card glass upload-card">
      <h2 className="card-title">
        <span aria-hidden="true">📸</span>
        <span>{t('leaf_image')}</span>
      </h2>

      <div
        className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
        onClick={handleBrowseClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        aria-label="Upload leaf photograph"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleBrowseClick();
          }
        }}
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            className="preview-img"
            alt="Uploaded leaf preview"
          />
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon" aria-hidden="true">🍃</div>
            <p className="upload-text">{t('upload_text')}</p>
            <p className="upload-hint">{t('upload_hint')}</p>
            <span className="upload-formats">JPG, PNG — max 10 MB</span>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png"
        className="file-input-hidden"
        onChange={handleFileChange}
      />

      <button
        type="button"
        className="btn btn-secondary btn-sm mt-2"
        onClick={handleBrowseClick}
      >
        {selectedFile ? 'Change File' : t('browse_file')}
      </button>
    </div>
  );
};
