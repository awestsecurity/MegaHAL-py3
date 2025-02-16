# For chatbot functions - install megahal
from megahal import *
# For text to speach - install pyttsx3
import pyttsx3
# For Left/Right Speaker Balance - install pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

whosline = 0
speaking = 0
convolength = 10
convostep = 0
speaker = ""

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
        volume.SetChannelVolumeLevel(0, -22, None) # Left
        volume.SetChannelVolumeLevel(1, avoidspeakerblowout, None) # Right
    else:
        volume.SetChannelVolumeLevel(0, avoidspeakerblowout, None) # Left
        volume.SetChannelVolumeLevel(1, -22, None) # Right

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

#The main loop
def converse():
    global convostep
    global convolength
    global whosline
    currentline = "Hello, I'd like to talk to you about death."
    sayWithFemaleVoice(currentline)
    print (currentline)
    while (convostep <= convolength):
        speaker = "Jannlee: " if whosline == 0 else "Chromise: "
        convostep += 1
        if (whosline == 0):
            currentline = leander.get_reply(currentline)
            print ("Leander: "+currentline) 
            sayWithMaleVoice(currentline)
            whosline = 1
        else: 
            currentline = chromis.get_reply(currentline)
            print ("Chromise: "+currentline) 
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
converse()  
        