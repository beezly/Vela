import time
import numpy as np
import pyaudio
import lib.config as config
from lib.config import log

ext_gui = None
stream = None
p = pyaudio.PyAudio()

def get_audio_devices():
  #print( "get audio" )
  global p
  numdevices = p.get_device_count()
  #for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
  audio_options = 'Default'
  for i in range (0,numdevices):
    device_info = p.get_device_info_by_host_api_device_index(0,i)
    if device_info.get('maxInputChannels')>0:
      name = device_info.get('name')
      audio_options += ','  + name
  #print ( audio_options )
  return audio_options

def microphone_register_gui( gui ):
  global ext_gui
  ext_gui = gui
  
def reset_microphone_device():
  global stream
  if stream is not None:
    stream.stop_stream()
    stream.close()
    stream = None

def start_stream(callback):
  global stream, p, ext_gui

  id = -1
  
  while id == -1:
    try:
      id=p.get_default_input_device_info()['index']
    except IOError:
      log('Cannot find microphone.')
      time.sleep( 5 )
	  
  frames_per_buffer = int(config.settings["configuration"]["MIC_RATE"] / config.settings["configuration"]["FPS"])

  overflows = 0
  prev_ovf_time = time.time()
  prev_time = time.time()
  adjustment_factor = 0.0
  while True:
    try:
      if stream is None:
        numdevices = p.get_device_count()
        #for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
        for i in range (0,numdevices):
          device_info = p.get_device_info_by_host_api_device_index(0,i)
          if device_info.get('maxInputChannels')>0:
            log( "Audio Device Found : " + device_info.get('name'), 4 )
            if device_info.get('name')==config.settings["configuration"]["MIC_NAME"]:
              id=i
              log( "Found Requested Microphone : " + device_info.get('name'), 3 )
        
        stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=config.settings["configuration"]["MIC_RATE"],
                input=True,
                input_device_index = id,
                frames_per_buffer=frames_per_buffer)
                
      time2 = time.time()
      if config.uses_audio :
        y = np.fromstring(stream.read(frames_per_buffer), dtype=np.int16)
        y = y.astype(np.float32)
        prev_time = time.time()
      else:
        y = 0
        desired_sleep = 1.0/config.settings["configuration"]["FPS"]
        last_loop = time.time() - prev_time
        if abs(last_loop - desired_sleep) > 0.0005: 
          if last_loop > desired_sleep:
            adjustment_factor -= 0.0005
          else:
            adjustment_factor += 0.0005
        sleep_time = desired_sleep + adjustment_factor
        prev_time = time.time()
        time.sleep( max( 0, sleep_time ) )
      callback(y)
      
      
    except IOError:
      overflows += 1
      if time.time() > prev_ovf_time + 1:
        prev_ovf_time = time.time()
        if config.settings["configuration"]["USE_GUI"]:
          ext_gui.label_error.setText('Audio buffer has overflowed {} times'.format(overflows))
        else:
          log('Audio buffer has overflowed {} times'.format(overflows))
  stream.stop_stream()
  stream.close()
  p.terminate()
