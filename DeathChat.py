from threading import Event, Thread
from megahal import *
import pyttsx3

whosline = 0
speaking = 0
convolength = 10
convostep = 0

def onEnd(name, completed):
    print ('Line Complete:', completed)
    speaking = 0

engine = pyttsx3.init()
engine.connect('finished-utterance', onEnd)
voices = engine.getProperty('voices')

anthony = MegaHAL()
dena = MegaHAL()
anthony.train('DeathTraining.trn')
dena.train('DeathTraining.trn')

def sayWithMaleVoice(line):
    engine.setProperty('rate', 125)
    engine.setProperty('voice',voices[0].id)
    engine.say(line)
    speaking = 1
    engine.runAndWait()
    
def sayWithFemaleVoice(line):
    engine.setProperty('rate', 150)
    engine.setProperty('voice',voices[1].id)  
    engine.say(line)
    speaking = 1
    engine.runAndWait()

def converse():
    global convostep
    global convolength
    global whosline
    currentline = "Hello, I'd like to talk to you about death."
    sayWithFemaleVoice(currentline)
    print (currentline)
    while (convostep <= convolength):
        convostep += 1
        if (whosline == 0):
            currentline = anthony.get_reply(currentline)
            sayWithMaleVoice(currentline)
            whosline = 1
        else: 
            currentline = anthony.get_reply(currentline)
            sayWithFemaleVoice(currentline)
            whosline = 0
        print (currentline)
    print("Conversation has concluded.")
    saveAndQuit()
    
def saveAndQuit():
    anthony.sync()
    anthony.close()
    dena.sync()
    dena.close()
  
converse()  
        