sudo pip install flask
sudo pip install Flask-PyMongo
sudo pip install pydub
sudo pip install bcrypt
sudo pip install google-cloud
sudo pip install --upgrade google-cloud-speech
sudo pip install flask-cors
sudo pip install soundfile
sudo pip install numpy
sudo pip install flask-socketio
sudo pip install eventlet
sudo pip install scipy
sudo pip install matplotlib

export FLASK_APP=flaskMiddleWare.py
export FLASK_DEBUG=true

$dir = [string](Get-Location) + "\external_modules\libav-x86\usr\bin\"
$Env:Path = $Env:Path + ";$dir"

$ffmpeg = [string](Get-Location) + "\ffmpeg\bin"
$Env:Path = $Env:Path + ";$ffmpeg"