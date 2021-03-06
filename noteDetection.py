'''Module containing all the useful functions used in noteDetection.ipnb notebook.'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy import signal
from scipy.signal import find_peaks
from pydub import AudioSegment
from pydub.playback import play
import os
from math import log2, pow

plt.style.use('ggplot')

## -------------------------------- 1. Plotting --------------------------------
def plotTimeSignal(filePath):
    '''Plot signal wrt time.'''
    # Get data
    rate, data = wav.read(filePath)
    
    # Get sampling information
    Fs = rate # sample rate
    T = 1/Fs # sampling period
    t = np.shape(data)[0] / rate # seconds of sampling
    N = Fs*t # total points in signal

    t_vec = np.linspace(0,t,N) # time vector for plotting
    
    plt.xlabel('time (s)')
    plt.ylabel('Amplitude')
    plt.plot(t_vec,data[:,1])
    
    return

def plotFT(filePath):
    '''Plot signal's FT'''
    # Get data
    rate, data = wav.read(filePath)
    
    # Get sampling information
    Fs = rate # sample rate
    T = 1/Fs # sampling period
    t = np.shape(data)[0] / rate # seconds of sampling
    N = Fs*t # total points in signal
    
    # fourier transform and frequency domain
    Y_k = np.fft.fft(data[:,1])[0:int(N/2)]/N # FFT function from numpy
    Y_k[1:] = 2*Y_k[1:] # need to take the single-sided spectrum only
    Pxx = np.abs(Y_k) # be sure to get rid of imaginary part
    f = (1/N) * Fs * np.arange((int(N/2))) # frequency vector

    # plotting
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency [Hz]')
    plt.xlim((20,5000)) #to change if needed
    
    plt.plot(f,Pxx,linewidth=2)
    
    return

def plotTimeAndFT(filePath):
    '''Plot both signal wrt time and signal's FT in the same figure.'''
    plt.figure()
    
    plt.subplot(211)
    plotTimeSignal(filePath)
    
    plt.subplot(212)
    plotFT(filePath)
    
    plt.show()
    return

def plotEnvelope(t_vec, YY, N, show = 0):
    peaks, _ = find_peaks(YY, distance= (N / 50))
    plt.xlabel('time (s)')
    plt.ylabel('Amplitude')
    plt.plot(t_vec,YY)
    t_vec_peaks = t_vec[peaks] # syntax to only retrieve the chosen indexes
    plt.plot(t_vec_peaks, YY[peaks], "--", label='envelope')
    plt.legend()
    plt.savefig('static/temp/envelope.png', dpi=150)
    if show == 1:
        plt.show()
    return

## -------------------------------- 3. Detecting silence parts --------------------------------
def getIdxEnvelope(YY_amplitude, N):
    ''' returns the INDEX of YY_amplitude considered as peaks'''
    idx_peaks, _ = find_peaks(YY_amplitude, distance= (N / 50)) # The 100 has been empiricaly chosen.
    return idx_peaks

def getPlayingTimestamps(data, rate, show = 0):
    '''From data and rate (extracted from wav.read), returns lNotesTimestamps which is a list of 2-elts tuples such as (silenceStart, silenceEnd).'''
    
    YY_amplitude = data[:,1] # contains the list of amplitudes taken in each 
    
    # Get sampling information
    Fs = rate # sample rate
    T = 1/Fs # sampling period
    t = np.shape(data)[0] / rate # seconds of sampling
    N = int(Fs*t) # total points in signal
    

    t_vec = np.linspace(0,t,N) # time vector for plotting
    
    # Silent parts related
    maxAmplitude = np.amax(YY_amplitude)
    print("maxAmplitude", maxAmplitude)

    startThreshold = maxAmplitude / 25 # can be changed if needed
    endThreshold = maxAmplitude / 100 # allows to prevent to detect too many silent parts
    lNotesTimestamps = []
    
    # Now let's get the envelope
    idx_peaks = getIdxEnvelope(YY_amplitude, N)
    t_vec_peaks = t_vec[idx_peaks]
    YY_peaks = YY_amplitude[idx_peaks]
    
    # ------------------------------------------------------------------------------------------------------------
    
    # Strategy: Let's browse through the amplitude array and each time we get below startThreshold,
    # it means that a new "silent part" is starting.
    
    hasNoteBegun = False
    timeStart = 0
    timeEnd = 0
    
    for idx, amplitude in np.ndenumerate(YY_peaks):
        if not(hasNoteBegun): # if we still haven't detected a note part...
            if abs(amplitude) >= startThreshold:
                hasNoteBegun = True
                timeStart = t_vec_peaks[idx[0]] #idx is a 1D tuple
        else: # ie "if hasNoteBegun"
            if abs(amplitude) < endThreshold: 
                hasNoteBegun = False # the note has ended!
                timeEnd = t_vec_peaks[idx[0]]
                
                # We can now add the timestamps in lNotesTimestamps
                lNotesTimestamps.append((timeStart,timeEnd))
    
    # if when we've finished browsing YY_amplitude, a note has begun but not ended, we'll add it manually.
    if hasNoteBegun: # thus the note hasn't ended yet...
        hasNoteBegun = False
        timeEnd = t_vec[-1]
        lNotesTimestamps.append((timeStart,timeEnd))
    
    # Amplitude wrt to time
    plt.xlabel('time (s)')
    plt.ylabel('Amplitude')
    plt.plot(t_vec_peaks, YY_peaks, 'b', label='signal')
    
    # Let's plot the horizontal lines that allow to define silent parts.
    
    n = np.shape(t_vec_peaks)[0]
    YY_startThreshold = [startThreshold for _ in range(n)]
    YY_endThreshold = [endThreshold for _ in range(n)]
    
    plt.plot(t_vec_peaks, YY_startThreshold, 'g-', label='YY_startThreshold')
    plt.plot(t_vec_peaks, YY_endThreshold, 'c-', label='YY_endThreshold')
    
    for tuple_timestamp in lNotesTimestamps:
        for timestamp in tuple_timestamp:
            plt.axvline(x = timestamp, color = 'orange', linewidth = 2)
    
    plt.legend()
    plt.savefig('static/temp/notesDetected.png', dpi=150)
    if show == 1:
        plt.show()

    return lNotesTimestamps

## -------------------------------- 4. Spectral Analysis --------------------------------
def pitch(freq):
    '''Returns a string giving the note played and its octave.'''
    A4 = 440
    C0 = A4*pow(2, -4.75)
    #name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    name = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
    
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)

## -------------------------------- 5. Getting the played notes in several trimmed audioSegments --------------------------------
def getIdxFromList(t_vec_list, lPlayingTimestamps):
    lIdx = []
    for timestamp_tuple in lPlayingTimestamps:
        t_start = t_vec_list.index(timestamp_tuple[0])
        t_end = t_vec_list.index(timestamp_tuple[1])
        lIdx.append((t_start,t_end))
    return lIdx

def exportTrimmedNotesAsWav(fileName, filePath, rate, YY_amplitude, lPlayingTimestamps):
    '''Also returns a list of the trimmed audio file paths.'''
    print("Number of notes = ", len(lPlayingTimestamps))
    print("\n")
    
    lTrimmedPaths = []
    
    for idx,tuple_timestamp in enumerate(lPlayingTimestamps):
        t_start, t_end = tuple_timestamp
        
        # Warning: One need to convert s to ms
        t_start *= 1000
        t_end *= 1000
        duration = t_end - t_start
        
        # Trimming audio
        padding = AudioSegment.silent(duration=duration)
        segment = AudioSegment.from_wav(filePath)[t_start:t_end] # from s to ms!!
        segment = padding.overlay(segment)
        
        # Set frame rate
        segment = segment.set_frame_rate(rate)
        
        # Export as wav
        exportFileName = "static/temp/trimmed/"+fileName[:-4]+"_"+str(idx)+'.wav'
        lTrimmedPaths.append(exportFileName)
        segment.export(exportFileName, format='wav')
        
    return lTrimmedPaths

def getFundamentalAndPlot(idx, subploatShape, filePath):
    '''Prepare to plot the subploats wrt time / FT of the idx-nth note.'''
    
    ## Retrieving useful data
    
    rate, data = wav.read(filePath)
    
    # Get sampling information
    Fs = rate # sample rate
    T = 1/Fs # sampling period
    t = np.shape(data)[0] / rate # seconds of sampling
    N = Fs*t # total points in signal
    
    # fourier transform and frequency domain
    Y_k = np.fft.fft(data[:,1])[0:int(N/2)]/N # FFT function from numpy
    Y_k[1:] = 2*Y_k[1:] # need to take the single-sided spectrum only
    Pxx = np.abs(Y_k) # be sure to get rid of imaginary part
    f = (1/N) * Fs * np.arange((int(N/2))) # frequency vector

    t_vec = np.linspace(0,t,np.shape(data)[0]) # time vector for plotting
    
    
    ## ------ Plotting wrt time: ------
    plt.subplot(int(subploatShape + str(2*idx + 1)))

    plt.xlabel('time (s)')
    plt.ylabel('Amplitude')
    plt.title('Note #' + str(idx + 1))
    plt.plot(t_vec,data[:,1])
    
    ## Getting fundamental frequency
    freq_fundamental = f[Pxx.argmax()]
    


    ## ------ Plotting FT: ------
    plt.subplot(int(subploatShape + str(2*idx + 2)))

    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude')
    plt.title(str(freq_fundamental)+' Hz')
    plt.xlim((20,5000)) #to change if needed
    
    plt.plot(f,Pxx,linewidth=2)
    
    return freq_fundamental

def processTrimmedNotes(lTrimmedPaths, show = 0):
    '''Returns a list of the different notes' frequences.'''
    n = len(lTrimmedPaths) # number of detected notes
    lFreq = []

    if len(lTrimmedPaths) == 0:
        print("Pas de notes détectées!")
        return []
    
    else:
        # We want a subploat with str(n) lines and 2 columns.
        subploatShape = str(n) + '2'
        print('subploatShape = ', subploatShape)
        
        fig = plt.figure()
        
        for idx, filePath in enumerate(lTrimmedPaths):
            lFreq.append(getFundamentalAndPlot(idx, subploatShape, filePath))
        
        fig.set_size_inches(15, 6 * n)
        print("on va l enregistrer")
        plt.savefig('static/temp/processed_figure.png', dpi=200)
        if show == 1:
            plt.show()
        return lFreq

## -------------------------------- 6. Synthesis Function --------------------------------
def getListNotes(fileName):
    ''' Given a fileName of a file in data/temp/ directory, \\
        computes the list of the detected notes (and their octave).'''
    filePath = "static/temp/" + fileName #path of the file

    # ---------------- Getting data ----------------
    rate, data = wav.read(filePath)

    # Computing useful variables for what comes next
    YY_amplitude = data[:,1] # contains the list of amplitudes taken in each 
    
    # Get sampling information
    Fs = rate # sample rate
    T = 1/Fs # sampling period
    t = np.shape(data)[0] / rate # seconds of sampling
    N = int(Fs*t) # total points in signal
    
    t_vec = np.linspace(0,t,N) # time vector for plotting

    # To get the envelope graph (optional)
    plotEnvelope(t_vec, YY_amplitude, N, show = 0)

    # ---------------- Analysing signal ----------------
    # Finding the timestamps that delimit the played notes
    lPlayingTimestamps = getPlayingTimestamps(data, rate)
    print("lPlayingTimestamps = ", lPlayingTimestamps)

    # Exporting the trimmed files AND getting the list of the paths pointing to these latter
    lTrimmedPaths = exportTrimmedNotesAsWav(fileName, filePath, rate, YY_amplitude, lPlayingTimestamps)

    print("lTrimmedPaths = ", lTrimmedPaths)
    # Getting the list of the frequencies of each delimited note
    lFreq = processTrimmedNotes(lTrimmedPaths, show = 0) # do not execute plt.show()

    # Getting the list of notes (as strings) that corresponds to those frequencies
    lNotes = [pitch(freq) for freq in lFreq]
    
    return lNotes