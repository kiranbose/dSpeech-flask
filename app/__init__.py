from flask import Flask

app = Flask(__name__)

from app import routesHandler

if (__name__ == "app"):
    app.run()