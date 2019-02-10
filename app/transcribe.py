#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the REST API for batch
processing.

Example usage:
    python transcribe.py resources/audio.wav
    python transcribe.py gs://cloud-samples-tests/speech/brooklyn.flac
"""

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
from app import threads, uploader

# [END import_libraries]
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "https://00e9e64bac4ef41886e0c211906cd70165e83390a355500be4-apidata.googleusercontent.com/download/storage/v1/b/dspeech-deploy.appspot.com/o/dspeechRamesh-b2ddeb411159.json?qk=AD5uMEt7gV2O6PgynU16YElF_I09kZaUA1nU2MNF1sfYpKRrOkJs0_Gl8CvBTUA5j06H1kRKUjW4SE_3B0ZKPJKsI_xoVtEL3lnQga708tQi0YkkyuUqNd2noz4l7-Qb9U6Cv2ftSi-mrPfvJ81AjrzJXEhUk-0q_rsudYKPNbazYKwIkiw2UOf0aH0bCdi0hVB0zPsdPxIRMxaXS3B3VtJJ-Kf4NFuGBTy1bv1Iw9ZChIfZtMsbRC_MTpaoBteJbzQZLort9crsoa2GWMZBlXbaEUJxYHMcUhvN49mXYrjSLrSKLeSCoj3txUB32ihGqBiwXf0WSMP86Cp0n3YsMLnyTSvuFvaEhi-trypjIpZFYx5inGdcHihRy4_fFoAvjMD-KLU4rcjHJg-gG0PWaJui64ko9dHopB_jYH2JUW6iWaAFRZCIoR66WGLeyfcLMIq1xSaL5JjFgsqLGKMXlPa2m0sDHHnMmvu5Sla7xaWO6zibBOpOTk7N51_ETDVOsgTJcvAfNj-ZcRE-YhrcTHI0VOV2AiQoTwb3C-97Y_vk0QYNoOgy-Sm1s-wBzUhmPhz8BERIZKF-I_9lfzBY8dpZ3masn21wLf7m7h47O4lnCMQn8NQ4krLxKQEc35PWc5KXGonwrS06K81hVHqRWTNwTYDrq3eE6bNNLVvww1wXcdVBt-BSvKKk5_tgebV7Gnkq3Fmo_dGbLEE5Pm1al0Gx85eUvUVnemgKExoTt0E8Lw5cG8ZR9QWbR2SDcFhJpeU089-vQryKhxASKeQP6phqM3yjq2uO65pVzoK8b4qZERkdCNODTog"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./connection.json"

# FFMPEG_PATH = os.path.abspath(os.path.join('./ffmpeg/bin/ffmpeg.exe'))
# FFPROBE = os.path.abspath(os.path.join('./ffmpeg/bin/ffprobe.exe'))
# AudioSegment.converter = FFMPEG_PATH
# AudioSegment.ffmpeg = FFMPEG_PATH
# AudioSegment.ffprobe = FFPROBE


# [START def_transcribe_file]
def transcribe_file(fileName):
    """Convert given audio file to single channel."""
    monoFileName = uploader._safe_filename('mono.wav')
    print(monoFileName)
    print(AudioSegment)
    sound = AudioSegment.from_file('./' + fileName)
    print(sound)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    duration_in_milliseconds = len(sound)
    sound.export(monoFileName, format='wav')
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    # [START migration_sync_request]
    # [START migration_audio_config_file]
    with io.open(monoFileName, 'rb') as audio_file:
        content = audio_file.read()
        gcs_uri = uploader.upload_file(content, monoFileName, 'audio/wav')
        plotGraph(monoFileName, gcs_uri)

    audio = types.cloud_speech_pb2.RecognitionAudio(content=content)
    config = types.cloud_speech_pb2.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-IN')
    # [END migration_audio_config_file]

    # [START migration_sync_response]
    response = client.recognize(config, audio)
    # [END migration_sync_request]
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    text = ''
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        text += u'{}'.format(result.alternatives[0].transcript)
        if(len(result.alternatives) > 0):
            text += ' '
    # [END migration_sync_response]
    return [duration_in_milliseconds, text, gcs_uri]
# [END def_transcribe_file]


# [START def_transcribe_gcs]
def transcribe_gcs(gcs_uri):
    """Transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # [START migration_audio_config_gcs]
    audio = types.cloud_speech_pb2.RecognitionAudio(uri=gcs_uri)
    config = types.cloud_speech_pb2.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code='en-US')
    # [END migration_audio_config_gcs]

    response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
# [END def_transcribe_gcs]


# def encodeAndSaveWAVFile(speech_file):
#     gcsFileUrl = speech_file.split('.')[0] + '.wav'
#     sound = AudioSegment.from_file(speech_file)
#     sound = sound.set_channels(1)
#     sound.export(gcsFileUrl, format='wav')
#     newThread = threads.GraphPlotterThread(speech_file)
#     newThread.setName('plotter')
#     newThread.run()


def plotGraph(fileName, gcs_uri):
    newThread = threads.GraphPlotterThread(fileName, gcs_uri)
    newThread.setName('plotter')
    newThread.run()