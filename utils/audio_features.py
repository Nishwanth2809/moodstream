from pydub import AudioSegment
import numpy as np

def extract_audio_features(file_path):
    audio = AudioSegment.from_file(file_path)
    samples = np.array(audio.get_array_of_samples())

    # Tempo estimation (very basic amplitude peaks)
    amplitude = np.abs(samples)
    peaks = np.where(amplitude > amplitude.mean() * 1.5)[0]
    tempo = len(peaks) / (len(samples) / audio.frame_rate)

    # Pitch estimation (FFT peak)
    fft = np.fft.fft(samples)
    freqs = np.fft.fftfreq(len(fft))
    peak_freq = abs(freqs[np.argmax(np.abs(fft))]) * audio.frame_rate

    return round(tempo, 2), round(peak_freq, 2)
