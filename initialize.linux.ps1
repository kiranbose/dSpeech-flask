sudo pip3 install flask
sudo pip3 install Flask-PyMongo
sudo pip3 install pydub
sudo pip3 install bcrypt
sudo pip3 install google-cloud
sudo pip3 install --upgrade google-cloud-speech
sudo pip3 install flask-cors
sudo pip3 install soundfile
sudo pip3 install numpy
sudo pip3 install flask-socketio
sudo pip3 install eventlet
sudo pip3 install scipy
sudo pip3 install matplotlib

export FLASK_APP=flaskMiddleWare.py
export FLASK_DEBUG=true

$dir = [string](Get-Location) + "\external_modules\libav-x86\usr\bin\"
$Env:Path = $Env:Path + ";$dir"

$ffmpeg = [string](Get-Location) + "\ffmpeg\bin"
$Env:Path = $Env:Path + ";$ffmpeg"