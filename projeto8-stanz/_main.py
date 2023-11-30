import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter


class Encoder:
    @staticmethod
    def generate_audio_file(filename):
        sample_rate = 44100
        duration = 4
        frequency_1, frequency_2 = (1336, 697)

        time_series = np.linspace(0, duration, int(
            sample_rate * duration), endpoint=False)

        amplitude = 1
        signal_1 = amplitude * np.sin(2 * np.pi * frequency_1 * time_series)
        signal_2 = amplitude * np.sin(2 * np.pi * frequency_2 * time_series)

        combined_signal = signal_1 + signal_2

        # Save the generated audio to a WAV file
        wavfile.write(filename, sample_rate,
                      combined_signal.astype(np.float32))

    @staticmethod
    def filter_and_save_audio(input_filename, output_filename):
        # Read the WAV file
        sample_rate, audio_data = wavfile.read(input_filename)

        # Define a high-pass filter to remove frequencies above 4000 Hz
        nyquist_freq = 0.5 * sample_rate
        cutoff_freq = 4000.0  # 4000 Hz cutoff
        b, a = butter(4, cutoff_freq / nyquist_freq, btype='high')

        # Apply the filter to the audio data
        filtered_audio = lfilter(b, a, audio_data)

        # Save the filtered audio to a new WAV file
        wavfile.write(output_filename, sample_rate,
                      filtered_audio.astype(np.float32))


    @staticmethod
    def am_modulate_and_save_audio(input_filename, output_filename, carrier_frequency):
        # Read the filtered audio
        sample_rate, audio_data = wavfile.read(input_filename)

        # Generate a carrier signal (sine wave) with the specified carrier frequency
        time_series = np.linspace(0, len(audio_data) / sample_rate, len(audio_data), endpoint=False)
        # carrier_signal = np.sin(2 * np.pi * carrier_frequency * time_series)
        carrier_signal = np.sin(2 * np.pi * carrier_frequency * time_series - np.pi/2)  # Subtract pi/2 to start at 0

        # Modulate the audio by multiplying it with the carrier signal
        modulated_audio = audio_data * carrier_signal
        max_amplitude = np.max(np.abs(modulated_audio))  # Find the maximum absolute value in the audio signal
        normalized_audio = modulated_audio / max_amplitude  # Normalize the modulated audio by scaling all points within [-1, 1]

        # Save the modulated audio to a new WAV file
        wavfile.write(output_filename, sample_rate, normalized_audio.astype(np.float32))


class Decoder:
    @staticmethod
    def am_demodulate_and_save_audio(input_filename, output_filename, carrier_frequency):
        # Read the AM modulated audio
        sample_rate, modulated_audio = wavfile.read(input_filename)

        # Generate a carrier signal (sine wave) with the same carrier frequency
        time_series = np.linspace(0, len(modulated_audio) / sample_rate, len(modulated_audio), endpoint=False)
        carrier_signal = np.sin(2 * np.pi * carrier_frequency * time_series - np.pi/2)  # Subtract pi/2 to start at 0

        # Demodulate the audio by multiplying it with the carrier signal
        demodulated_audio = modulated_audio * carrier_signal

        # Calculate the envelope of the demodulated audio (absolute value)
        envelope = np.abs(demodulated_audio)

        # Normalize the demodulated audio using the envelope
        max_amplitude = np.max(envelope)
        normalized_audio = demodulated_audio / max_amplitude

        # Define a low-pass filter to remove high-frequency components
        nyquist_freq = 0.5 * sample_rate
        cutoff_freq = 4000.0  # Adjust as needed
        b, a = butter(4, cutoff_freq / nyquist_freq, btype='low')

        # Apply the filter to the normalized demodulated audio
        filtered_audio = lfilter(b, a, normalized_audio)

        # Save the demodulated audio to a new WAV file
        wavfile.write(output_filename, sample_rate, filtered_audio.astype(np.float32))


# Usage example
if __name__ == "__main__":
    encoder = Encoder()
    encoder.generate_audio_file("generated_audio.wav")
    encoder.filter_and_save_audio("generated_audio.wav", "filtered_audio.wav")
    encoder.am_modulate_and_save_audio("filtered_audio.wav", "am_modulated_audio.wav", carrier_frequency=14000)

    decoder = Decoder()
    decoder.am_demodulate_and_save_audio("am_modulated_audio.wav", "demodulated_audio.wav", carrier_frequency=14000)
