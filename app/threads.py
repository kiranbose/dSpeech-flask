
# [START import_libraries]
import argparse
import io, os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment
from scipy.io import wavfile
from matplotlib import pyplot as plt
import numpy as np
from threading import Thread
from pymongo import MongoClient

client = MongoClient()
db = client.speechDatabase
pfCollection = db.powerFrequency

# [END import_libraries]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./valiant-sandbox-218317-79c90d68c7aa.json"

FFMPEG_PATH = os.path.abspath(os.path.join('./ffmpeg/bin/ffmpeg.exe'))
FFPROBE = os.path.abspath(os.path.join('./ffmpeg/bin/ffprobe.exe'))
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffmpeg = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE

class GraphPlotterThread(Thread):
    def __init__(self, fileName):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.fileName = fileName
 
 
    def run(self):
        samplerate, data = wavfile.read(self.fileName)
        # Make the plot
        power = 20*np.log10(np.abs(np.fft.rfft(data[:])))
        frequencies = np.abs(np.linspace(0, samplerate/2.0, len(power)))
        frequency = format(np.argmax(frequencies))
        times = np.arange(len(power))/float(samplerate)
        # You can tweak the figsize (width, height) in inches
        plt.figure(figsize=(30, 4))
        plt.plot(times, power, color='r') 
        # plt.plot(times, frequencies, color='b') 
        plt.xlim(times[0], times[-1])
        plt.xlabel('time (s)')
        plt.ylabel('power')
        ax = plt.subplot(111)
        x = np.arange(10)
        ax.plot(x, 1 * x, label='Power', color='r')
        ax.plot(x, 2 * x, label='Frequency %s Hz'%frequency , color='b')
        ax.legend()
        # You can set the format by changing the extension
        # like .pdf, .svg, .eps
        plt.savefig(self.fileName.split('.')[0] + '_plot.png', dpi=100)
        # plt.show()
        pfCollection.insert_one({
            'stereoFilePath': self.fileName,
            'avgPower': np.average(power),
            'avgFrequency': np.average(frequencies),
            'sampleRate': samplerate
        })


class CompareGraphGenerator(Thread):
    def __init__(self, record1, record2):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.fileName1 = record1['stereoFilePath']
        self.fileName2 = record2['stereoFilePath']
        self.targeFilePath = self.fileName1.split('.')[0] + '+' + record2['fileName'].split('.')[0]
 
    def run(self):
        samplerate1, data1 = wavfile.read(self.fileName1)
        samplerate2, data2 = wavfile.read(self.fileName2)
        # Make the plot
        
        power1 = 20*np.log10(np.abs(np.fft.rfft(data1[:])))
        power2 = 20*np.log10(np.abs(np.fft.rfft(data2[:])))
        # frequency1 = np.abs(np.linspace(0, samplerate1/2.0, len(power1)))
        # frequency2 = np.abs(np.linspace(0, samplerate2/2.0, len(power2)))
        times1 = np.arange(len(power1))/float(samplerate1)
        times2 = np.arange(len(power2))/float(samplerate2)
        # You can tweak the figsize (width, height) in inches
        plt.figure(figsize=(30, 4))
        plt.plot(times1, power1, color='r') 
        plt.plot(times2, power2, color='g') 
        # plt.fill_between(times, frequency, color='g') 
        plt.xlim(times1[0] + times2[0], times2[-1] + times2[0])
        plt.xlabel('time (s)')
        plt.ylabel('power')
        ax = plt.subplot(111)
        x = np.arange(10)
        ax.plot(x, 1 * x, label='User Audio', color='r')
        ax.plot(x, 2 * x, label='Sample Audio', color='g')
        ax.legend()
        # You can set the format by changing the extension
        # like .pdf, .svg, .eps
        plt.savefig(self.targeFilePath + '.png', dpi=100)
        # plt.show()
