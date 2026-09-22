import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Camera, FlipHorizontal, RotateCcw, Check, X, AlertCircle } from 'lucide-react';
import { useI18n } from '../../context/I18nContext';

interface CameraCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (file: File) => void;
  onFallbackToFile: () => void;
}

export const CameraCaptureModal: React.FC<CameraCaptureModalProps> = ({
  isOpen,
  onClose,
  onCapture,
  onFallbackToFile,
}) => {
  const { language } = useI18n();
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [capturedPreview, setCapturedPreview] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoadingCamera, setIsLoadingCamera] = useState<boolean>(true);

  // Stop active media stream tracks
  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignore track stop errors
        }
      });
      streamRef.current = null;
    }
  }, []);

  // Start live camera stream
  const startCamera = useCallback(async () => {
    stopStream();
    setIsLoadingCamera(true);
    setErrorMessage(null);
    setCapturedBlob(null);
    setCapturedPreview(null);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setErrorMessage(
        'Live camera access is not supported by your browser or environment. Please use device file picker.'
      );
      setIsLoadingCamera(false);
      return;
    }

    try {
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: { ideal: facingMode },
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {
          // Play request might be interrupted by unmount
        });
      }
      setIsLoadingCamera(false);
    } catch (err: any) {
      console.warn('[CameraCaptureModal] getUserMedia error:', err);
      let msg = 'Could not access device camera.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera permission was denied. Please allow camera permissions in your browser settings.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No camera device found on this system.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = 'Camera is already in use by another application.';
      }
      setErrorMessage(msg);
      setIsLoadingCamera(false);
    }
  }, [facingMode, stopStream]);

  // Effect to manage stream on open/close
  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopStream();
    }

    return () => {
      stopStream();
    };
  }, [isOpen, startCamera, stopStream]);

  // Handle capture shutter click
  const handleCapture = () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // If front camera, mirror image for natural selfie orientation
    if (facingMode === 'user') {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob) {
          setCapturedBlob(blob);
          const preview = URL.createObjectURL(blob);
          setCapturedPreview(preview);
          stopStream();
        }
      },
      'image/jpeg',
      0.94
    );
  };

  // Confirm photo and send to parent
  const handleUsePhoto = () => {
    if (!capturedBlob) return;
    const filename = `leaf_capture_${Date.now()}.jpg`;
    const file = new File([capturedBlob], filename, { type: 'image/jpeg' });
    onCapture(file);
    handleClose();
  };

  // Retake photo
  const handleRetake = () => {
    if (capturedPreview) {
      URL.revokeObjectURL(capturedPreview);
    }
    setCapturedBlob(null);
    setCapturedPreview(null);
    startCamera();
  };

  // Flip camera between front & rear
  const handleFlipCamera = () => {
    setFacingMode((prev) => (prev === 'environment' ? 'user' : 'environment'));
  };

  const handleClose = () => {
    if (capturedPreview) {
      URL.revokeObjectURL(capturedPreview);
    }
    setCapturedBlob(null);
    setCapturedPreview(null);
    stopStream();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="camera-modal-title"
      style={{
        zIndex: 1000,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        className="modal-card glass"
        style={{
          width: '100%',
          maxWidth: '560px',
          background: '#0d1d16',
          border: '1px solid rgba(56, 161, 105, 0.4)',
          borderRadius: '20px',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8)',
          padding: '20px',
          boxSizing: 'border-box',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Camera size={20} color="#34d399" />
            <h3
              id="camera-modal-title"
              style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}
            >
              {language === 'mr' ? 'पीक/पानाचे छायाचित्र घ्या' : language === 'hi' ? 'फसल/पत्ती का फोटो लें' : 'Capture Leaf Photograph'}
            </h3>
          </div>
          <button
            type="button"
            onClick={handleClose}
            aria-label="Close camera"
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#e2e8f0',
              cursor: 'pointer',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Viewfinder / Video Container */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            aspectRatio: '4 / 3',
            background: '#050c09',
            borderRadius: '14px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(56, 161, 105, 0.25)',
          }}
        >
          {errorMessage ? (
            <div style={{ padding: '24px', textAlign: 'center', color: '#fca5a5' }}>
              <AlertCircle size={36} color="#ef4444" style={{ marginBottom: '10px' }} />
              <p style={{ margin: '0 0 16px 0', fontSize: '0.9rem', lineHeight: 1.5 }}>
                {errorMessage}
              </p>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => {
                  handleClose();
                  onFallbackToFile();
                }}
                style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              >
                📁 Open File / Device Picker
              </button>
            </div>
          ) : capturedPreview ? (
            /* Review captured photo */
            <img
              src={capturedPreview}
              alt="Captured leaf snapshot"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : (
            /* Live camera stream */
            <>
              {isLoadingCamera && (
                <div style={{ position: 'absolute', color: '#34d399', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div className="btn-spinner" style={{ width: '28px', height: '28px', borderColor: '#34d399', borderTopColor: 'transparent' }} />
                  <span style={{ fontSize: '0.85rem' }}>Initializing camera...</span>
                </div>
              )}
              <video
                ref={videoRef}
                playsInline
                autoPlay
                muted
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  transform: facingMode === 'user' ? 'scaleX(-1)' : 'none',
                }}
              />

              {/* Viewfinder Alignment Reticle Overlay */}
              <div
                style={{
                  position: 'absolute',
                  inset: '16px',
                  border: '2px dashed rgba(52, 211, 153, 0.65)',
                  borderRadius: '12px',
                  pointerEvents: 'none',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.3)',
                }}
              >
                <div style={{ position: 'absolute', top: '10px', left: '10px', background: 'rgba(0,0,0,0.6)', padding: '3px 8px', borderRadius: '4px', fontSize: '0.72rem', color: '#6ee7b7' }}>
                  🟢 LIVE
                </div>
                <div style={{ position: 'absolute', bottom: '10px', width: '100%', textAlign: 'center', color: '#cbd5e1', fontSize: '0.76rem', textShadow: '0 1px 3px rgba(0,0,0,0.8)' }}>
                  Align leaf or infected area in center
                </div>
              </div>
            </>
          )}
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px', paddingTop: '4px' }}>
          {capturedPreview ? (
            /* Buttons shown when review photo */
            <>
              <button
                type="button"
                onClick={handleRetake}
                className="btn btn-secondary"
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  fontSize: '0.9rem',
                }}
              >
                <RotateCcw size={16} />
                <span>{language === 'mr' ? 'पुन्हा घ्या' : language === 'hi' ? 'फिर से लें' : 'Retake'}</span>
              </button>

              <button
                type="button"
                onClick={handleUsePhoto}
                className="btn btn-primary"
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  fontSize: '0.9rem',
                  background: '#38a169',
                }}
              >
                <Check size={16} />
                <span>{language === 'mr' ? 'हा फोटो वापरा' : language === 'hi' ? 'यह फोटो चुनें' : 'Use Photo'}</span>
              </button>
            </>
          ) : !errorMessage ? (
            /* Controls during live viewfinder */
            <>
              <button
                type="button"
                onClick={handleFlipCamera}
                title="Switch front / rear camera"
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '10px',
                  color: '#e2e8f0',
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  fontSize: '0.82rem',
                }}
              >
                <FlipHorizontal size={16} />
                <span>Flip</span>
              </button>

              {/* Shutter Button */}
              <button
                type="button"
                onClick={handleCapture}
                disabled={isLoadingCamera}
                style={{
                  flex: 1,
                  background: '#38a169',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '12px',
                  padding: '12px 18px',
                  fontWeight: 700,
                  fontSize: '0.94rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  cursor: isLoadingCamera ? 'default' : 'pointer',
                  boxShadow: '0 4px 14px rgba(56, 161, 105, 0.4)',
                }}
              >
                <Camera size={18} />
                <span>{language === 'mr' ? 'फोटो टिपून घ्या' : language === 'hi' ? 'फोटो खींचें' : 'Capture Photo'}</span>
              </button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};
