import React, { useRef, useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { CameraCaptureModal } from './CameraCaptureModal';

interface UploadCardProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({ selectedFile, onFileSelect }) => {
  const { t, language } = useI18n();
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

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

  const handleCameraClick = () => {
    // If WebRTC getUserMedia is available in current browser context, launch live viewfinder
    if (navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
      setIsCameraOpen(true);
    } else {
      // Fallback directly to native device camera/gallery file picker
      cameraInputRef.current?.click();
    }
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
            <span className="upload-formats">JPG, PNG, WebP — max 10 MB</span>
          </div>
        )}
      </div>

      {/* Hidden File Picker Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="file-input-hidden"
        onChange={handleFileChange}
      />

      {/* Hidden Native Camera Direct Capture Input */}
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="file-input-hidden"
        onChange={handleFileChange}
      />

      {/* Action Buttons: Camera + File Gallery */}
      <div className="upload-actions-row mt-2" style={{ display: 'flex', gap: '8px' }}>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          style={{ flex: 1, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
          onClick={handleCameraClick}
          title="Capture photo using device camera"
        >
          <span>📸</span>
          <span>{language === 'mr' ? 'कॅमेरा उघडा' : language === 'hi' ? 'कैमरा खोलें' : 'Take Photo'}</span>
        </button>

        <button
          type="button"
          className="btn btn-secondary btn-sm"
          style={{ flex: 1, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
          onClick={handleBrowseClick}
          title="Select photo from file gallery"
        >
          <span>📁</span>
          <span>{selectedFile ? (language === 'mr' ? 'फोटो बदला' : language === 'hi' ? 'फोटो बदलें' : 'Change') : t('browse_file')}</span>
        </button>
      </div>

      {/* Live Interactive Camera Viewfinder Modal */}
      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={(file) => {
          processFile(file);
        }}
        onFallbackToFile={() => {
          cameraInputRef.current?.click();
        }}
      />
    </div>
  );
};
