#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Process, Pipe
import subprocess
import os
import bokeh
import threading
import git
import signal
import time

class jupterNotebook:
    '''
    The jupterNotebook class represents a single juypter notebook.
    A jupterNotebook object has all the information needed to server the notebook to a bokeh server.
    '''
    def __init__(self, fileName, filePath, port):

        self.fileName = fileName
        self.filePath = filePath
        self.port = port

    '''
    Serves the Bokeh application to the websocket. Starts
    the server on its on thread.
    '''
    def serveBokehApp(self):
        def startServer(self):
            BOKEH_ALLOW_WS_ORIGIN='ns1007523.ip-51-81-155.us:'+str(self.port)
            subprocess.call(['python3', '-m', 'bokeh', 'serve',  self.filePath, '--port', str(self.port),
                 '--allow-websocket-origin=ns1007523.ip-51-81-155.us:'+str(self.port)])

        thread1 = threading.Thread(target=startServer, args=(self,))
        thread1.start()

    '''
    Shuttdowns the Bokeh server using npx.
    '''
    def shutdown(self):
        subprocess.call(['npx', 'kill-port', str(self.port)])

    '''
    Getter function to return the link to the Bokeh server.
    '''
    def getPortLink(self):
        return ('http://ns1007523.ip-51-81-155.us:'+str(self.port)+'/'+self.fileName.replace(".ipynb",""))

    '''
    Getter for the port that the Bokeh server will be deployed on.
    '''
    def getPort(self):
        return self.port


class handlePorts:
    '''
    This class keeps tracks of what ports have been assinged to jupterNotebook objects
    and which ports are open to be assigned to a new notebook.
    '''
    def __init__(self, firstPortNumber):
        self.firstPortNumber = firstPortNumber
        self.openPorts = []
        self.NextNewPort = firstPortNumber

    '''
    Assigns a new port. This method opens up the next port in line to be used to the web.

    returns: new_port, an integer, the number of the new port that has been spun up.
    '''
    def assignNewPort(self):
        # Check if any previously shut down ports were shut down.
        if (len(self.openPorts)>0):
            new_port = self.openPorts[0]
            self.openPorts.remove(new_port)
            subprocess.call(['sudo', 'ufw', 'allow', str(new_port)])
            return new_port
        else:
            self.NextNewPort = self.NextNewPort+1
            subprocess.call(['sudo', 'ufw', 'allow', str(self.NextNewPort-1)])
            return(self.NextNewPort-1)
    '''
    This method adds back old port numbers to the list of avalible ports.
    It stops allowing web traffic to the port.
    '''
    def addBackOldPort(self, oldPort):
        subprocess.call(['sudo', 'ufw', 'deny', str(oldPort)])
        self.openPorts.append(oldPort)


class jupterNoteBookList:
    '''
    This class represents a colection of jupterNotebook objects that corrispond to the .ipynb files in a git hub repo.
    '''
    def __init__(self, gitHubLink, localRepoPath, portStart):
        self.gitHubLink = gitHubLink
        self.localRepoPath = localRepoPath
        self.servedFiles = 0
        self.notebookDict = {}
        self.g = git.cmd.Git(localRepoPath)
        self.g.pull(self.gitHubLink)
        self.fileArray = []
        self.BokehLinkDict = {}
        self.ports = handlePorts(portStart+1)

    '''
    This functions does one Git Pull of the repositroy to update the local files. It then updates the file list
    by searching through the file name list and adding or deleting file names as needed.
    '''
    def updateLocalFiles(self):
        self.g.pull(self.gitHubLink)
        thisPullFiles = []
        for root, dirs, files in os.walk(self.localRepoPath):
            if (".git" not in root):
                for f in files:
                    if(".ipynb" in f):
                        thisPullFiles.append(f)
                    if("requirements.txt" in f):
                        subprocess.call(['pip', 'install', '-r', f])

        #delete files and jupterNotebook objects from the array that have been deleted in the repo
        for oldFile in self.fileArray:
            if(oldFile not in thisPullFiles):
                self.fileArray.remove(oldFile)
                self.ports.addBackOldPort(self.notebookDict[oldFile].getPort())
                self.notebookDict[oldFile].shutdown()
                self.notebookDict.pop(oldFile)
                self.BokehLinkDict.pop(oldFile)

        # Create a new jupterNotebook object for each new .ipynb file
        for newFile in thisPullFiles:
            if newFile not in self.fileArray:
                self.fileArray.append(newFile)
                port = self.ports.assignNewPort()
                jnb = jupterNotebook(newFile, self.localRepoPath + "/" + newFile, port)
                jnb.serveBokehApp()
                self.notebookDict[newFile] = jnb
                self.BokehLinkDict[newFile] = jnb.getPortLink()

    '''
    Driver function for the running the updateFiles method as a thread.
    '''
    def loopUpdate(self):
        def loopFunction():
            while(True):
                self.updateLocalFiles()

        threadUpdateFiles = threading.Thread(target=loopFunction, args=())
        threadUpdateFiles.start()

    '''
    Getter function for the fileArray contaning all the repositorys file names.
    '''
    def getFileArray(self):
        return self.fileArray

    '''
    Getter function for the BokehLinkDict which contains all .ipynb files and the
    link to the port where bokeh server lives.
    '''
    def getBokehLinkDict(self):
        return self.BokehLinkDict


j1 = jupterNoteBookList(os.environ['GIT_REPO_LINK'], os.environ['REPO_LOCAL_DIR'], int(os.environ['PORT_START']))

j1.loopUpdate()

def f(child_conn):
    child_conn.send(j1.getBokehLinkDict())
    child_conn.close()
