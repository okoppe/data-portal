from flask import Flask, render_template, request, Response, send_from_directory
import subprocess
import os
from multiprocessing import Process,Queue,Pipe
from server_pipe_test import f

subprocess.call(['sudo', 'ufw', 'allow', os.environ['PORT_START']])

selectedValue2 = " "


app = Flask(__name__)
#hone directory
@app.route("/")
def index():
    parent_conn,child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()

    BokehLinkDictFlaskCopy = parent_conn.recv()
    p.join()
    return render_template("index.html", noteBookNames=list(BokehLinkDictFlaskCopy.keys()), BokehLinkDictFlaskCopy = BokehLinkDictFlaskCopy,
        bool_files = len(BokehLinkDictFlaskCopy.keys()), selectedValue = "select a notebook")

#path for veiwing data set inline
@app.route('/chooseDataSet/<noteBookName>', methods = ['POST', 'GET'])
def chooseDataSet(noteBookName):
    global selectedValue2
    selectedValue2 = noteBookName

    parent_conn,child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()

    BokehLinkDictFlaskCopy2 = parent_conn.recv()
    p.join()

    return render_template("index.html", noteBookNames=list(BokehLinkDictFlaskCopy2.keys()),
        bool_files = len(BokehLinkDictFlaskCopy2.keys()), selectedValue = selectedValue2,
        linkToBokeh = BokehLinkDictFlaskCopy2[selectedValue2])

#path for downloading file
@app.route("/download", methods=['GET', 'POST'])
def download():

    return send_from_directory(directory=os.environ['REPO_LOCAL_DIR'], path=selectedValue2, as_attachment=True)
    #return send_from_directory(directory="/home/owenkoppe/Juypter-Notebook-Repo", path=selectedValue2, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ['PORT_START']), debug=True)
