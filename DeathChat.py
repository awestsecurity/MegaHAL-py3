import sys
import time
# For chatbot functions - install megahal
from megahal import *
# For text to speach - install pyttsx3
import pyttsx3
# For Left/Right Speaker Balance - install pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#set from command line argument
convolength = 20

#tracking variables
whosline = 0
speaking = 0
convostep = 0
countTime = False
endTime = 5

#for left/right channel control
volume = None
maxvolume = 0
mono = False

# function called when a speaker is finished talking out loud
def onEnd(name, completed):
    #print ('Line Complete:', completed)
    speaking = 0
    
def SetupAudio():
    global volume
    global maxvolume
    global mono
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    mono = True if (volume.GetChannelCount() < 2) else False
    maxvolume = volume.GetChannelVolumeLevel(0)
    print (f"Audio setup complete with {volume.GetChannelCount()} channels and max volume: {maxvolume}. Mono is set to {mono}")
    
def SwitchAudioChannel(channelid):
    global volume
    global maxvolume
    global mono
    avoidspeakerblowout = -3.0
    if mono:
        return false
    if channelid == 0:
        volume.SetChannelVolumeLevel(0, -65.0, None) # Left
        volume.SetChannelVolumeLevel(1, maxvolume, None) # Right
    else:
        volume.SetChannelVolumeLevel(0, maxvolume, None) # Left
        volume.SetChannelVolumeLevel(1, -65.0, None) # Right

engine = pyttsx3.init()
engine.connect('finished-utterance', onEnd)
voices = engine.getProperty('voices')

leander = MegaHAL(None,'leander.brn',None)
chromis = MegaHAL(None,'chromis.brn',None)
leander.train('DeathTraining.trn')
chromis.train('DeathTraining.trn')

def sayWithMaleVoice(line):
    engine.setProperty('rate', 115)
    engine.setProperty('voice',voices[0].id)
    SwitchAudioChannel(0)
    speaking = 1
    engine.say(line)
    engine.runAndWait()
    
def sayWithFemaleVoice(line):
    engine.setProperty('rate', 135)
    engine.setProperty('voice',voices[1].id)  
    SwitchAudioChannel(1)
    speaking = 1
    engine.say(line)
    engine.runAndWait()

# take the arguement for conversation length if given. sys.argv[0] is the python file name
def parseSysArgs():
    global convolength
    global countTime
    global endTime
    global timeStart
    #print(sys.argv)
    if len(sys.argv) == 1:
        return
    if len(sys.argv) == 3:
        if sys.argv[1] == '-l':
            convolength = int(sys.argv[2])
            print(f"setting conversation length to {convolength} lines.")
        elif sys.argv[1] == '-t':
            countTime = True
            endTime = int(sys.argv[2])
            print(f"setting conversation length to {endTime} seconds.")

#The main loop
def converse():
    global convostep
    global convolength
    global whosline
    global countTime
    global endTime
    #Begin conversation
    currentline = "Hello, I'd like to talk to you about death."
    sayWithFemaleVoice(currentline)
    print (currentline)
    #Use time to determine length of conversation
    if(countTime):
        timeStart = time.time()
        currentTime = time.time() - timeStart
        while (currentTime < endTime):
            currentTime = time.time() - timeStart
            print(currentTime)
            if (whosline == 0):
                currentline = leander.get_reply(currentline)
                print ("Leander: "+currentline) 
                sayWithMaleVoice(currentline)
                whosline = 1
            else: 
                currentline = chromis.get_reply(currentline)
                print ("Chromis: "+currentline) 
                sayWithFemaleVoice(currentline)
                whosline = 0
    #Use number of lines to determine length of conversation (DEFAULT)
    else:
        while (convostep < convolength):
            convostep += 1
            if (whosline == 0):
                currentline = leander.get_reply(currentline)
                print ("Leander: "+currentline) 
                sayWithMaleVoice(currentline)
                whosline = 1
            else: 
                currentline = chromis.get_reply(currentline)
                print ("Chromis: "+currentline) 
                sayWithFemaleVoice(currentline)
                whosline = 0
    print("Conversation has concluded.")
    saveAndQuit()
    
def saveAndQuit():
    leander.sync()
    leander.close()
    chromis.sync()
    chromis.close()
  
SetupAudio()
parseSysArgs()
converse()  
volume.SetChannelVolumeLevel(0, maxvolume, None) # Left
volume.SetChannelVolumeLevel(1, maxvolume, None) # Right
        