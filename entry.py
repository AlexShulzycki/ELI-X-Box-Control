import os

#os.chdir("./server")
print(os.getcwd())
from server import main
main.serve()