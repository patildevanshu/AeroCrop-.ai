/**
 * AeroCrop.ai — Web Speech Synthesis Utility (Vernacular Voice Advisory)
 * Provides hands-free audio narration in Marathi, Hindi, and English.
 */

export const speakText = (
  text: string,
  lang: 'en' | 'mr' | 'hi' = 'mr',
  onEnd?: () => void,
  onError?: (err: any) => void
): boolean => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    console.warn('SpeechSynthesis is not supported in this browser environment.');
    if (onError) onError('Speech synthesis not supported');
    return false;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  if (!text.trim()) return false;

  const utterance = new SpeechSynthesisUtterance(text);
  
  // Set BCP-47 language tag
  const langTagMap: Record<string, string> = {
    mr: 'mr-IN',
    hi: 'hi-IN',
    en: 'en-IN',
  };
  utterance.lang = langTagMap[lang] || 'en-IN';
  utterance.rate = 0.92; // Slightly slower for agricultural clarity
  utterance.pitch = 1.0;

  // Try to find a matching voice installed on user's device/browser
  const voices = window.speechSynthesis.getVoices();
  const targetPrefix = langTagMap[lang] || 'en';
  const matchingVoice = voices.find(
    (v) => v.lang.toLowerCase().replace('_', '-').startsWith(targetPrefix.toLowerCase().slice(0, 2))
  );

  if (matchingVoice) {
    utterance.voice = matchingVoice;
  }

  if (onEnd) {
    utterance.onend = () => onEnd();
  }
  if (onError) {
    utterance.onerror = (e) => {
      console.warn('Speech synthesis error:', e);
      onError(e);
    };
  }

  window.speechSynthesis.speak(utterance);
  return true;
};

export const stopSpeech = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
};

export const isSpeaking = (): boolean => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    return window.speechSynthesis.speaking;
  }
  return false;
};
