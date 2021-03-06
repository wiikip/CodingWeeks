#list_note de 1 à 7 (do->si)
import numpy as np
from pydub import AudioSegment
import random

from scipy.io import wavfile
import os

list_notes = []


def create_audio_file(lNotes,lvl,anticache):
    notes =[]
    for i in lNotes:
        notes.append(AudioSegment.from_wav("static/musicNotes/" + i + '.wav'))

    audiofile = sum(notes[i] for i in range(len(notes)))
    audiofile.export("./static/musicNotes/"+ str(lvl) + str(anticache) + ".wav", format="wav")

    return audiofile

