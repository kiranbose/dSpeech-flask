pip install flask
pip install Flask-PyMongo
pip install pydub
pip install bcrypt
pip install google-cloud
pip install --upgrade google-cloud-speech
pip install flask-cors
pip install soundfile
pip install numpy
pip install flask-socketio
pip install eventlet
pip install scipy
pip install matplotlib

set FLASK_APP=flaskMiddleWare.py
set FLASK_DEBUG=true

$dir = [string](Get-Location) + "\external_modules\libav-x86\usr\bin\"
$Env:Path = $Env:Path + ";$dir"

$ffmpeg = [string](Get-Location) + "\ffmpeg\bin"
$Env:Path = $Env:Path + ";$ffmpeg"