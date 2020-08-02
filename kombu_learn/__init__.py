import os
from config import Config


root_path = os.getcwd()
global conf
conf = Config(root_path)
conf.from_pyfile("config")