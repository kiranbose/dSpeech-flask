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
from app import uploader

from six.moves.urllib.request import urlopen

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
    def __init__(self, fileName, gcs_uri):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.fileName = fileName
        self.gcs_uri = gcs_uri
 
 
    def run(self):
        samplerate, data = wavfile.read('./' + self.fileName)
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
        path = self.fileName.split('.')[0] + '_plot.png'
        plt.savefig(path, dpi=100)

        with io.open(path, 'rb') as plot_file:
            content = plot_file.read()
            plotUrl = uploader.upload_file(content, path, 'image/png')
            uploader.deleteFile('./' + path)


        # plt.show()
        pfCollection.insert_one({
            'gcsFileUrl': self.gcs_uri,
            'avgPower': np.average(power),
            'avgFrequency': np.average(frequencies),
            'sampleRate': samplerate,
            'plotUrl': plotUrl
        })


class CompareGraphGenerator(Thread):
    def __init__(self, record1, record2, targetFileName):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.fileName1 = record1['gcsFileUrl']
        self.fileName2 = record2['gcsFileUrl']
        self.targetFileName = targetFileName
 
    def run(self):
        
        file1 = urlopen(self.fileName1)
        compareFile1 = open('./compareFile1.wav', 'wb')
        compareFile1.write(file1.read())
        samplerate1, data1 = wavfile.read('./compareFile1.wav')

        file2 = urlopen(self.fileName2)
        compareFile2 = open('./compareFile2.wav', 'wb')
        compareFile2.write(file2.read())        
        samplerate2, data2 = wavfile.read('./compareFile1.wav')

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
        plt.savefig('./' + self.targetFileName, dpi=100)
        with io.open('./' + self.targetFileName, 'rb') as audio_file:
            content = audio_file.read()
            uploader.upload_file(content, self.targetFileName, 'image/png')
            uploader.deleteFromLocal('./' + self.targetFileName)
            
        uploader.deleteFromLocal('./' + self.fileName1)
        uploader.deleteFromLocal('./' + self.fileName2)
        # plt.show()
