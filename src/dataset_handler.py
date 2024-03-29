import numpy as np
import librosa # NOTE: librosa is built on top of matplotlib
import librosa.display
import random
import math
import subprocess

from scipy.io.wavfile import write
from glob import glob
from config import PATH_TO_STEMS, PATH_TO_WAV
from wav_handler import WavHandler

class DatasetHandler:
    def __init__(self, path_to_stems: str=PATH_TO_STEMS, path_to_wav: str=PATH_TO_WAV) -> None:
        self.path_stems = path_to_stems
        self.path_wav = path_to_wav

    def stemToWav(self) -> None:
        """
        Create wav files of the stems if they don't exist yet
        """
        if len(glob(self.path_wav)) <= 0:
            subprocess.run(["musdbconvert", self.path_stems, self.path_wav])
        else:
            print("'wav' folder already exists!")
    
    def createBassless(self) -> None:
        """
        Creates another wav file called bassless.wav for each song in the train and test set
        """

        test_dir = glob(self.path_wav + r"\*")[0]
        train_dir = glob(self.path_wav + r"\*")[1]

        test_songs = glob(test_dir + r"\*")
        train_songs = glob(train_dir + r"\*")

        for folder in [test_songs, train_songs]:
            for song in folder:
                if len(glob(song + "\\bassless.wav")) <= 0:
                    drums, sr = librosa.load(song + "\\drums.wav", sr = None)
                    vocals, _ = librosa.load(song + "\\vocals.wav", sr = None)
                    other, _ = librosa.load(song + "\\other.wav", sr = None)

                    write(song + "\\bassless.wav", sr, (drums + vocals + other)/3)
                    print("Writing at " + song + "\\bassless.wav")
                else:
                    print(f"'{song}\\bassless.wav' already exists!")

    def loadTrainInputWav(self):
        """
        Converts each input wav (mixture.wav) into WavHandler object and appends to an array to be returned
        """

        train_inputs = glob(self.path_wav + r"\train\*\mixture.wav")
        # print(self.path_wav + r"\train\*\mixture.wav")

        inputs = []

        for song in train_inputs:
            wav_handler = WavHandler(song)

            inputs.append(wav_handler.wav)

        return np.array(inputs) # (100, 1, 1)

    def loadTrainOutputWav(self):
        """
        Converts each expected output wav (bass.wav, bassless.wav) into WavHandler object and appends to an array to be returned
        """
        train_bass = glob(self.path_wav + r"\train\*\bass.wav")
        train_bassless = glob(self.path_wav + r"\train\*\bassless.wav")

        outputs = []

        for i in range(len(train_bass)): # train_bass and train_bassless have same length
            bass_wav = WavHandler(train_bass[i])
            bassless_wav = WavHandler(train_bassless[i])

            outputs.append(np.array([bass_wav.wav, bassless_wav.wav]))

        return np.array(outputs) # (100, 1, 2)

    def loadTestWav(self):
        """
        Converts each mixture.wav in test folder into WavHandler object and appends to an array to be returned
        """

        test_inputs = glob(self.path_wav + r"\test\*\mixture.wav")

        test = []

        for song in test_inputs:
            wav_handler = WavHandler(song)

            test.append(wav_handler.wav)

        return np.array(test) # (50, 1, 1)
    
    def writeTrainInputSpec(self): # https://stackoverflow.com/questions/53084637/how-do-you-open-npy-files
        """
        Writes computed segment spectrograms of each train input as a file named padded_spectrograms.npy
        """

        train_inputs = glob(self.path_wav + r"\train\*\mixture.wav")

        # array_segment_spec = []

        for song in train_inputs:
            if len(glob(song[:-11] + "padded_spectrograms.npy")) <= 0:
                obj = WavHandler(song)
                segments = obj.segmentWav()
                spectrograms = obj.computeSTFT(segments)
                padded_spectrograms = obj.zeroPadSTFT(spectrograms)

                # array_segment_spec.append(padded_spectrograms)
                np.save(song[:-11] + "padded_spectrograms.npy", padded_spectrograms)
            else:
                print(f"'{song[:-11]}padded_spectrograms.npy' already exists!")


        # return array_segment_spec
    
    def writeTrainOutputSpec(self):
        """
        Writes computed segment spectrograms of each train output as a file named bass_padded_spectrograms.npy and bassless_padded_spectrograms.npy
        """

        train_bass = glob(self.path_wav + r"\train\*\bass.wav")
        train_bassless = glob(self.path_wav + r"\train\*\bassless.wav")

        # array_segment_spec = []

        for i in range(len(train_bass)): # train_bass and train_bassless have same length
            if len(glob(train_bass[i][:-8] + "bass_padded_spectrograms.npy")) <= 0:
                bass_wav = WavHandler(train_bass[i])
                bass_segments = bass_wav.segmentWav()
                bass_spectrograms = bass_wav.computeSTFT(bass_segments)
                bass_padded_spectrograms = bass_wav.zeroPadSTFT(bass_spectrograms)

                np.save(train_bass[i][:-8] + "bass_padded_spectrograms.npy", bass_padded_spectrograms)
            else:
                print(f"'{train_bass[i][:-8]}bass_padded_spectrograms.npy' already exists!")

            if len(glob(train_bassless[i][:-12] + "bassless_padded_spectrograms.npy")) <= 0:
                bassless_wav = WavHandler(train_bassless[i])
                bassless_segments = bassless_wav.segmentWav()
                bassless_spectrograms = bassless_wav.computeSTFT(bassless_segments)
                bassless_padded_spectrograms = bassless_wav.zeroPadSTFT(bassless_spectrograms)
                
                np.save(train_bassless[i][:-12] + "bassless_padded_spectrograms.npy", bassless_padded_spectrograms)
            else:
                print(f"'{train_bassless[i][:-12]}bassless_padded_spectrograms.npy' already exists!")

            # array_segment_spec.append(np.array([bass_padded_spectrograms, bassless_padded_spectrograms]))

        # return array_segment_spec

    def writeTestSpec(self):
        """
        Writes computed segment spectrograms of each test input as a file named padded_spectrograms.npy
        """

        test_inputs = glob(self.path_wav + r"\test\*\mixture.wav")

        # array_segment_spec = []

        for song in test_inputs:
            if len(glob(song[:-11] + "padded_spectrograms.npy")) <= 0:
                obj = WavHandler(song)
                segments = obj.segmentWav()
                spectrograms = obj.computeSTFT(segments)
                padded_spectrograms = obj.zeroPadSTFT(spectrograms)

                # array_segment_spec.append(padded_spectrograms)
                np.save(song[:-11] + "padded_spectrograms.npy", padded_spectrograms)
            else:
                print(f"'{song[:-11]}padded_spectrograms.npy' already exists!")

        # return array_segment_spec

    def flattenArraySpec(self, array_spec: list): # https://stackoverflow.com/questions/33711985/flattening-a-list-of-numpy-arrays
        return np.concatenate(array_spec).ravel()
    
    def loadTrainInputSpec(self):
        """
        Loads padded segment spectograms of each train input wav
        """
        train_inputs = glob(self.path_wav + r"\train\*\padded_spectrograms.npy")

        array_segment_spec = []

        for segment_spec_path in train_inputs:
            segment_spec = np.load(segment_spec_path)

            array_segment_spec.append(segment_spec)

        return array_segment_spec


    def loadTrainOutputSpec(self):
        """
        Loads padded segment spectograms of each train output wav (bass, bassless)
        """
        train_output_bass = glob(self.path_wav + r"\train\*\bass_padded_spectrograms.npy")
        train_output_bassless = glob(self.path_wav + r"\train\*\bassless_padded_spectrograms.npy")

        array_segment_spec_tup = []

        for i in range(len(train_output_bass)):
            segment_spec_bass = np.load(train_output_bass[i])
            segment_spec_bassless = np.load(train_output_bassless[i])

            array_segment_spec_tup.append(np.array([segment_spec_bass, segment_spec_bassless]))

        return array_segment_spec_tup
