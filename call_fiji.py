import subprocess
from os.path import expanduser

#You have to change the directory according to your path of the FiJi.app directory

def callFJ(path):
    home = expanduser("~")
    dir = "/home/markus/Fiji.app/"
    print(path)
    subprocess.check_call(['./ImageJ-linux64', '--ij2', '--run', '/home/markus/Progs/iGEM_Darmstadt_Technik/fijitest.py', 'mypath="{}/" '.format(path)], cwd=dir)
