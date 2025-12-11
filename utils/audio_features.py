import wave
import numpy as np

def extract_audio_features(file_path):
    with wave.open(file_path, "rb") as wav_file:
        n_channels = wav_file.getnchannels()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        audio_frames = wav_file.readframes(n_frames)

    audio = np.frombuffer(audio_frames, dtype=np.int16)

    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)

    audio = audio.astype(np.float32)
    audio /= np.max(np.abs(audio)) + 1e-6

    amplitude = np.abs(audio)
    peaks = np.where(amplitude > amplitude.mean() * 2.0)[0]
    duration = len(audio) / framerate
    tempo = len(peaks) / duration if duration > 0 else 0

    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(fft), 1 / framerate)
    peak_idx = np.argmax(np.abs(fft[:len(fft)//2]))
    peak_freq = abs(freqs[peak_idx])

    return round(tempo, 2), round(peak_freq, 2)
