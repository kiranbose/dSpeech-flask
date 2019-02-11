# from bookshelf import get_model, storage

import datetime
import six
from google.cloud import storage
from flask import Blueprint, redirect, render_template, request, \
    url_for
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
from threading import Timer

import os

from app import app

app.config['PROJECT_ID'] = "dspeechRamesh"
app.config['ALLOWED_EXTENSIONS'] = set(['wav', 'mp3', 'png'])
app.config['CLOUD_STORAGE_BUCKET'] = "dspeech"


def _get_storage_client():
    return storage.Client(
        project=app.config['PROJECT_ID'])

    
def _check_extension(filename, allowed_extensions):
    if ('.' not in filename or
            filename.split('.').pop().lower() not in allowed_extensions):
        raise BadRequest(
            "{0} has an invalid name or extension".format(filename))


def _safe_filename(filename):
    """
    Generates a safe filename that is unlikely to collide with existing objects
    in Google Cloud Storage.
    ``filename.ext`` is transformed into ``filename-YYYY-MM-DD-HHMMSS.ext``
    """
    filename = secure_filename(filename)
    print("filename==", filename)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, date, extension)


# [START upload_file]
def upload_file(file_stream, filename, content_type):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """
    _check_extension(filename, app.config['ALLOWED_EXTENSIONS'])

    client = _get_storage_client()
    bucket = client.bucket(app.config['CLOUD_STORAGE_BUCKET'])
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    if os.path.isfile(fileName):
        os.remove(fileName)
    else:    ## Show an error ##
        print("Error: %s file not found" % fileName)

    return url
# [END upload_file]

def deleteFromLocal(fileName):
    #Timer(10.0, confirmDelete, (fileName))
    if os.path.isfile(fileName):
        os.remove(fileName)
    else:    ## Show an error ##
        print("Error: %s file not found" % fileName)

# def confirmDelete(fileName):
#     if os.name == 'posix':
#         os.system('sudo rm ' + fileName)
#     else:
#         os.remove(fileName)