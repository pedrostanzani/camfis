import numpy as np
from scipy.io import wavfile


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


class Decoder:
    pass


# Usage example
if __name__ == "__main__":
    encoder = Encoder()
    encoder.generate_audio_file("generated_audio.wav")
    encoder.filter_and_save_audio("generated_audio.wav", "filtered_audio.wav")
    encoder.am_modulate_and_save_audio("filtered_audio.wav", "am_modulated_audio.wav", carrier_frequency=14000)

    decoder = Decoder()
    decoder.am_demodulate_and_save_audio("am_modulated_audio.wav", "demodulated_audio.wav", carrier_frequency=14000)
