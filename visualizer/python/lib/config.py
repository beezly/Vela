"""Default settings and configuration for audio reactive LED strip"""
from __future__ import print_function
from __future__ import division
from PIL import Image
import os

uses_audio = False
uses_video = False

def log( msg, log_level = 0 ):
  if ( settings["configuration"]["LOG_LEVEL"] ) > log_level:
    print( msg )

use_defaults = {"configuration": True,                           # See notes below for detailed explanation
                "MQTT": True,
                "LiFX": True,
                "GUI_opts": True,
                "devices": True,
                "colors": True,
                "gradients": True,
                "qualities": True,
                "setting_topics": True,
                "setting_scales": True}

settings = {                                                      # All settings are stored in this dict

    "configuration":{  # Program configuration
                     'USE_GUI': True,                                                         # Whether to display the GUI
                     'LOG_LEVEL':  8,                                                         # How verbose is the console logging? 0 - 10 range, 0 being off, 10 being everything
                     'DISPLAY_FPS': False,                                                    # Whether to print the FPS when running (can reduce performance)
                     'MIC_RATE': 44100,                                                       # Sampling frequency of the microphone in Hz
                     'MIC_NAME': '',                                                          # Set input name or keep empty to use default input
                     'FPS': 50,                                                               # Desired refresh rate of the visualization (frames per second)
                     'MAX_BRIGHTNESS': 255,                                                   # Max brightness sent to LED strip
                     'N_ROLLING_HISTORY': 3,                                                  # Number of past audio frames to include in the rolling window
                     'MIN_VOLUME_THRESHOLD': 0.00000001,                                      # No music visualization displayed if recorded audio volume below threshold
                     #'LOGARITHMIC_SCALING': True,                                            # Scale frequencies logarithmically to match perceived pitch of human ear
                     "CHECK_DISPLAY": True,                                                   # Should we test the monitor state and send out messages over MQTT?
                     "USE_MULTICAST": False,                                                  # Should we use a multicast IP instead of unicast to individual IPs?
                     "USE_MQTT": True,                                                        # If true, take/issue commands via MQTT
                     "USE_MQTT_LED_STATE" : False,                                            # If true will set LED state to an MQTT topic.  Not really fast enough for realtime audio, but could be useful for other stuff?  Deprecated...
                     "MQTT_IP": "YOUR_MQTT_ADDRESS",                                          # MQTT IP
                     "MQTT_PORT": 1883,                                                       # MQTT Port
                     "USE_LIFX": False,                                                       # Should we broadcast visualight zones to lifx?
                     "MULTICAST_UDP_IP": "225.255.255.240",                                   # Multicast UDP IP
                     "SCREENGRAB_MAX_FPS": 30,                                                # Screengrabbing will be capped at this framerate for performance reasons
                     "SCREENGRAB_SCALE_FACTOR": 4,                                            # Should be somewhere between 3-6+, go higher with higher resolutions for faster performance
                     },
                     
    "MQTT":{
                     "MQTT_CMND_PREFIX":  "cmnd/visualizer/",                                 # The prefix for mqtt commands
                     "MQTT_STAT_PREFIX":  "stat/visualizer/",                                 # The prefix used for mqtt status
                     "MQTT_LIGHT_TOPIC":  "/data",                                            # Used if LED STATE is set to true - the same packet we'd set over UDP is set here.  
                     "MQTT_ENABLE_TOPIC": "/enable",                                          # Topic for enabling/disabling audio on any strips which have opted in.
                     "MQTT_SCHEME_TOPIC": "/scheme",                                          # Exit audio mode straight to a set scheme
                     "MQTT_POWER_TOPIC":  "/power",                                           # Exit audio mode to power on/off
                     "MQTT_DIMMER_TOPIC": "/dimmer",                                          # Dimmer brightness from 1-100
                     "MQTT_DEBUG_TOPIC":  "/debug",                                           # Debugging commands can be set on this from 1-255
                     "MQTT_DISPLAY_TOPIC": "/display",                                        # The display topic on/off
                     "MQTT_AUDIO_DEVICES_TOPIC": "/audio_devices",                            # A list of available audio devices
                     "MQTT_MICROPHONE_TOPIC": "/mic",                                         # Select a microphone command
                     "MQTT_COLOR_OPTIONS_TOPIC": "/color_options",                            # A list of available color options
                     "MQTT_PALETTE_OPTIONS_TOPIC": "/palette_options",                        # A list of available palette options
                     "MQTT_EFFECT_OPTIONS_TOPIC": "/effect_options",                          # A list of available effect options
                     "MQTT_EFFECT_BASE_TOPIC":          "/effect/",                           # The effect mode by name
                     "MQTT_EFFECT_MODE_TOPIC":          "mode",                               # The effect mode by name
                     "MQTT_EFFECT_SPEED_TOPIC":         "speed",                              # The speed of the effect	
                     "MQTT_EFFECT_BLUR_TOPIC":          "blur",                               # The blur of the effect
                     "MQTT_EFFECT_DECAY_TOPIC":         "decay",                              # The decay of the effect
                     "MQTT_EFFECT_WIDTH_TOPIC":         "width",                              # The width of the effect
                     "MQTT_EFFECT_MIRROR_TOPIC":        "mirror",                             # Whether to mirror the effect
                     "MQTT_EFFECT_SENSITIVITY_TOPIC":   "sensitivity",                        # The sensitivity of the effect
                     "MQTT_EFFECT_PALETTE_TOPIC":       "palette",                            # The palette of the effect	by name
                     "MQTT_EFFECT_COLOR_TOPIC":         "color",                              # Color Topic by NameError
                     "MQTT_EFFECT_COLOR_FLASH_TOPIC":   "color_flash",                        # Color Flash Topic by NameError
                     "MQTT_EFFECT_R_TOPIC":             "red",                                # Red Multiplier
                     "MQTT_EFFECT_G_TOPIC":             "green",                              # Green Multiplier
                     "MQTT_EFFECT_B_TOPIC":             "blue",                               # Blue Multiplier
                     "MQTT_EFFECT_FREQUENCY_MIN_TOPIC": "frequency_min",                      # Minimum Frequency
                     "MQTT_EFFECT_FREQUENCY_MAX_TOPIC": "frequency_max",                      # Maximum Frequency
                     "MQTT_EFFECT_COLOR_LOWS_TOPIC":    "lows_color",                         # Scroll Lows Color
                     "MQTT_EFFECT_COLOR_MIDS_TOPIC":    "mids_color",                         # Scroll Mids Color
                     "MQTT_EFFECT_COLOR_HIGH_TOPIC":    "high_color",                         # Scorll High Color 
                     "MQTT_EFFECT_CAPTURE_FPS_TOPIC":   "capturefps",                         # Visualight Capture FPS
                     "MQTT_EFFECT_CONTRAST_TOPIC":      "contrast",                           # Visualight Contrast
                     "MQTT_EFFECT_SATURATION_TOPIC":    "saturation",                         # Visualight Saturation
                     "MQTT_EFFECT_MIN_LEVEL_TOPIC":     "min_level",                          # Visualight Minimum Pixel Level
                     "MQTT_EFFECT_REVERSE_TOPIC":       "reverse",                            # Reverse Effect
                     "MQTT_EFFECT_FLIP_LR_TOPIC":       "flip_lr",                            # Flip L/R
                     "MQTT_EFFECT_QUALITY_TOPIC":       "quality",                            # Capture Quality
                     "MQTT_ZONE_BASE_TOPIC":            "/zones/",                            # Base topic for zones
                     "MQTT_ZONE_GLOBAL_TOPIC":          "zone_global",                        # General Avg Color 
                     "MQTT_ZONE_CENTER_TOPIC":          "zone_center",                        # Center of the Screen Avg Color 
                     "MQTT_ZONE_TOP_TOPIC":             "zone_top",                           # Top Avg Color
                     "MQTT_ZONE_RIGHT_TOPIC":           "zone_right",                         # Right Avg Color
                     "MQTT_ZONE_BOT_TOPIC":             "zone_bot",                           # Bot Avg Color
                     "MQTT_ZONE_LEFT_TOPIC":            "zone_left",                          # Left Avg Color                    
                     "MQTT_ZONE_GLOBAL_CUSTOM_TOPIC":   None,                                 # This topic is a complete MQTT topic for a custom recipient Example : "cmnd/sonoff_led/color"
                     "MQTT_ZONE_CENTER_CUSTOM_TOPIC":   None,                                 # This topic is a complete MQTT topic for a custom recipient Output in Hex : #FF0000
                     "MQTT_ZONE_TOP_CUSTOM_TOPIC":      None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_RIGHT_CUSTOM_TOPIC":    None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_BOT_CUSTOM_TOPIC":      None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_LEFT_CUSTOM_TOPIC":     None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_DISPLAY_CUSTOM_TOPIC":       None,                                 # This topic is a complete MQTT topic for a display on/off                     
                     "MQTT_ENABLE_PAYLOAD_ON":  "on",                                         # Payload for enabling audio mode
                     "MQTT_ENABLE_PAYLOAD_OFF": "off",                                        # Payload for disabling audio mode
                     "MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC": "/lights/",                         # LED Strips opt into audio mode via this topic via IP topic and available/unavailable payload
                     "MQTT_AVAILABLE_LIGHTS_IP_TOPIC": "/ip",                                 # The ip topic for each strip ie : stat/visualizer/[boardname]/lights/[name]/ip
                     "MQTT_AVAILABLE_LIGHTS_STATE_TOPIC": "/state",                           # The state topic for each strip ie : stat/visualizer/[boardname]/lights/[name]/state
                     "MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_AVAILABLE": "on",                   # LED Strip opt in avaiablility topic on
                     "MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_UNAVAILABLE": "off",                # LED Strip opt in avaiablility topic off
                     "MQTT_MONITOR_PAYLOAD_ON":  "on",                                        # Payload for monitor on
                     "MQTT_MONITOR_PAYLOAD_OFF": "off",                                       # Payload for monitor off
                     "MQTT_MONITOR_PAYLOAD_SUSPEND": "sleep",                                 # Payload for monitor sleep
                     "MQTT_TOPIC_QOS": 0,                                                     # QOS for topic    
            },
    "LiFX":{
                     "LIFX_NUMLIGHTS": None,                  # If the number of lights is known/specified it'll speed up discovery or None
                     "LIFX_DISCOVER_LIGHTS": False,           # Discover and list available lights - takes some time, directly adding lights by mac/ip is faster
                     "LIFX_GLOBAL_GROUP": None,               # Group name for the global light Ex: "Living Room" will trigger discovery
                     "LIFX_CENTER_GROUP": None,               # Group name for the center light
                     "LIFX_TOP_GROUP": None,                  # Group name for the top light
                     "LIFX_RIGHT_GROUP": None,                # Group name for the right light
                     "LIFX_BOT_GROUP": None,                  # Group name for the bot light
                     "LIFX_LEFT_GROUP": None,                 # Group name for the left light
                     "LIFX_GLOBAL_LIGHTS": None,              # List of Lights for the global light Ex: ["left light", "right light"] by name will trigger discovery
                     "LIFX_CENTER_LIGHTS": None,              # List of Lights for the center light or [["12:34:56:78:9a:bc", "192.168.0.2"]] for direct access
                     "LIFX_TOP_LIGHTS": None,                 # List of Lights for the top light
                     "LIFX_RIGHT_LIGHTS": None,               # List of Lights for the right light
                     "LIFX_BOT_LIGHTS": None,                 # List of Lights for the bot light
                     "LIFX_LEFT_LIGHTS": None,                # List of Lights for the left light
            },
                     
    "GUI_opts":{"Graphs":True,                                    # Which parts of the gui to show
                "Reactive Effect Buttons":True,
                "Non Reactive Effect Buttons":True,
                "Frequency Range":True,
                "Effect Options":True},

    # All devices and their respective settings. Indexed by name, call each one what you want.
    "devices":{"monitor":{
                      "configuration":{"TYPE": "ESP8266",                           # Device type (see below for all supported boards)
                                        # Required configuration for device. See below for all required keys per device
                                       "AUTO_DETECT": False,                        # Set this true if you're using windows hotspot to connect (see below for more info)
                                       "MAC_ADDR": "YOUR MAC ADDRESS HERE",         # MAC address of the ESP8266. Only used if AUTO_DETECT is True
                                       "UDP_IP": "YOUR_IP_HERE",                    # IP address of the ESP8266. Must match IP in ws2812_controller.ino - unused for MQTT
                                       "UDP_PORT": 7777,                            # Port number used for socket communication between Python and ESP8266
                                       "MAX_BRIGHTNESS": 255,                       # Max brightness of output (0-255) (my strip sometimes bugs out with high brightness)
                                         # Other configuration 
                                       "N_PIXELS": 100,                             # Number of pixels in the LED strip for visualization - will be remapped to the actual number by the ESP8266
                                       "N_PIXEL_OFFSET": 0,                         # How much to offset the edge/center of the effect.  Useful for rings and things where your physical strip start/endpoints aren't aligned to where you want the start/end of the effect
                                       "N_FFT_BINS": 24,                            # Number of frequency bins to use when transforming audio to frequency domain
                                       "MIN_FREQUENCY": 200,                        # Frequencies below this value will be removed during audio processing
                                       "MAX_FREQUENCY": 12000,                      # Frequencies above this value will be removed during audio processing
                                       "current_effect": "Spectrum",                # Currently selected effect for this board, used as default when program launches
                                       "light_array":{}                             # "[name]":{"ip":"[xxx.xxx.xxx.xxx]","state":"[on/off]",}
                                      },
    
                      # Configurable options for this board's effects go in this dictionary.
                      # Usage: config.settings["devices"][name]["effect_opts"][effect][option]
                      "effect_opts":{"Energy":    {"blur": 1,                       # Amount of blur to apply
                                                   "width":9,                       # Width of effect on strip
                                                   "r_multiplier": 1.0,             # How much red
                                                   "mirror": True,                  # Reflect output down centre of strip
                                                   "g_multiplier": 1.0,             # How much green
                                                   "b_multiplier": 1.0},            # How much blue
                                     "Wave":      {"color": "Red",                  # Colour of moving bit
                                                   "color_flash": "White",          # Colour of flashy bit
                                                   "width":5,                       # Initial length of colour bit after beat
                                                   "decay": 0.7,                    # How quickly the flash fades away 
                                                   "speed":2},                      # Number of pixels added to colour bit every frame
                                     "Spectrum":  {"r_multiplier": 1.0,             # How much red
                                                   "g_multiplier": 1.0,             # How much green
                                                   "b_multiplier": 1.0},            # How much blue
                                     "Wavelength":{"roll_speed": 0,                 # How fast (if at all) to cycle colour overlay across strip
                                                   "color_mode": "Spectral",        # Colour gradient to display
                                                   "mirror": False,                 # Reflect output down centre of strip
                                                   "reverse_grad": False,           # Flip (LR) gradient
                                                   "reverse": False,                # Reverse movement of gradient roll
                                                   "blur": 3.0,                     # Amount of blur to apply
                                                   "flip_lr":False},                # Flip output left-right
                                     "Scroll":    {"sensitivity": 2.0,              # Sensitivity of the effect
                                                   "lows_color": "Red",             # Colour of low frequencies
                                                   "mids_color": "Green",           # Colour of mid frequencies
                                                   "high_color": "Blue",            # Colour of high frequencies
                                                   "decay": 0.995,                  # How quickly the colour fades away as it moves
                                                   "speed": 4,                      # Speed of scroll
                                                   "mirror": True,                  # Reflect output down centre of strip
                                                   "r_multiplier": 1.0,             # How much red
                                                   "g_multiplier": 1.0,             # How much green
                                                   "b_multiplier": 1.0,             # How much blue
                                                   "blur": 0.2},                    # Amount of blur to apply
                                     "Power":     {"color_mode": "Spectral",        # Colour gradient to display
                                                   "s_count": 20,                   # Initial number of sparks
                                                   "color_flash": "White",          # Color of sparks
                                                   "mirror": True,                  # Mirror output down central axis
                                                   "flip_lr":False},                # Flip output left-right
                                     "Single":    {"color": "Purple"},              # Static color to show
                                     "Beat":      {"color": "Red",                  # Colour of beat flash
                                                   "decay": 0.7},                   # How quickly the flash fades away
                                     "Bars":      {"resolution":4,                  # Number of "bars"
                                                   "color_mode":"Spectral",         # Multicolour mode to use
                                                   "roll_speed":0,                  # How fast (if at all) to cycle colour colours across strip
                                                   "mirror": False,                 # Mirror down centre of strip
                                                   "reverse": False,                # Reverse movement of gradient roll
                                                   "flip_lr":False},                # Flip output left-right
                                     "Pulse":     {"sensitivity": 0.125,            # Sensitivity of the effect
                                                   "color_mode":"Spectral"          # Multicolour mode to use
                                                   },
                                     "Visualight":{
                                                   "blur": 0.6,                     # Gaussian Blur to be applied
                                                   "saturation": 1.1,               # How much color we use 
                                                   "gamma_r":2.1,                   # Gamma Red Adjustment
                                                   "gamma_g":2.2,                   # Gamma Green Adjustment
                                                   "gamma_b":2.1,                   # Gamma Blue Adjustment
                                                   "contrast":2.1,                  # How much contrast we use
                                                   "sensitivity": 0.5,              # Brightness of the effect
                                                   "decay": 0.6,                    # How much interpolation to do between frames
                                                   "bias_min": 1,                   # Minimum output level - for bias lighting, we may not want to go totally black
                                                   "roll": 0,                       # Offet for strip if it's not top left corner as the start - this will also be offset by the N_PIXEL_OFFSET, so alternatively you can set it globally there
                                                   "capturefps": 30,                # Maximum capture speed.  Will override the global one
                                                   "quality":"Hamming",             # The quality and therby speed of scaling, selected from the quality list below
                                                   "output_zones":False,            # Send general colored zones to MQTT/LiFX - for controlling discrete lights outside of the strip
                                                   },
                                     "Gradient":  {"color_mode":"Spectral",         # Colour gradient to display
                                                   "roll_speed": 0,                 # How fast (if at all) to cycle colour colours across strip
                                                   "blur": 0.1,                     # Amount of blur to apply
                                                   "mirror": False,                 # Mirror gradient down central axis
                                                   "reverse": False},               # Reverse movement of gradient
                                     "Fade":      {"color_mode":"Spectral",         # Colour gradient to fade through
                                                   "roll_speed": 1,                 # How fast (if at all) to fade through colours
                                                   "reverse": False},               # Reverse "direction" of fade (r->g->b or r<-g<-b)
                                     "Calibration":{"r": 100,
                                                    "g": 100,
                                                    "b": 100},
                                     "Larson Scanner":{
                                                       "color": "Red",              # Colour of beat flash
                                                       "decay": 0.25,               # How quickly it fades away
                                                       "roll_speed": 2,             # How fast it moves
                                                       "blur": 0.25,                # Fade at the edges
                                                       "width": 12,                 # Fade at the edges
                                                       "r_multiplier": 1.0,         # How much red
                                                       "g_multiplier": 1.0,         # How much green
                                                       "b_multiplier": 1.0,         # How much blue
                                                       "mirror": False,             # Mirror down central axis
                                                      },
                                     }
                                  }
              # Add any additional devices here (copy/paste above with a new name) for it's own visualizer
              },



    # Collection of different colours in RGB format
    "colors":{"Red":(255,0,0),
              "Coral":(245,87,50),
              "Orange":(255,40,0),
              "Yellow":(255,255,0),
              "Gold":(205,125,0),
              "Yellow Green":(143,240,27),
              "Green":(0,255,0),
              "Cyan":(0,255,205),
              "Turquoise":(0,206,249),
              "Blue":(0,0,255),
              "Light Blue":(1,247,161),
              "Sky Blue":(115,186,215),
              "Mauve":(32,5,32),
              "Purple":(80,5,252),
              "Pink":(255,0,148),
              "Blossom":(235,62,83),
              "Rose":(255,108,155),
              "White":(255,255,255),
              "Peach":(145,88,45),
              "Spring Green":(0,215,87),
              "Pale Green":(112,231,112),
              "Forest Green":(34,139,34)
              },

    # Multicolour gradients. Colours must be in list above
    "gradients":{"Spectral"  : ["Red", "Orange", "Yellow", "Green", "Light Blue", "Blue", "Purple", "Pink"],
                 "Dancefloor": ["Red", "Pink", "Purple", "Blue"],
                 "Sunset"    : ["Red", "Orange", "Gold", "Yellow"],
                 "Ocean"     : ["Forest Green", "Light Blue", "Blue"],
                 "Jungle"    : ["Green", "Red", "Orange"],
                 "Sunny"     : ["Yellow", "Light Blue", "Orange", "Blue"],
                 "Fruity"    : ["Orange", "Blue"],
                 "Peach"     : ["Orange", "Pink"],
                 "Rust"      : ["Gold", "Red"],
                 "Halloween" : ["Orange", "Mauve", "Orange", "Mauve"],
                 "Xmas"      : ["Red", "Green", "Red", "Green", "Red", "Green"],
                 "Sakura"    : ["Blossom", "Coral", "Rose", "Peach"],
                 "Forest"    : ["Spring Green", "Forest Green", "Green", "Pale Green", "Peach"]
                 },
                 
    # Collection of different colours in RGB format
    "qualities":{"Nearest"     : Image.NEAREST,
                 "Bilinear"    : Image.BILINEAR,
                 "Hamming"     : Image.HAMMING,
                 "Bicubic"     : Image.BICUBIC,
                 "Lanczos"     : Image.LANCZOS
                 },
    
    # Mapping of options to topics
    "setting_topics":{"current_effect"  : "MQTT_EFFECT_MODE_TOPIC",
                      "MIN_FREQUENCY"   : "MQTT_EFFECT_FREQUENCY_MIN_TOPIC",
                      "MAX_FREQUENCY"   : "MQTT_EFFECT_FREQUENCY_MAX_TOPIC",
                      "speed"           : "MQTT_EFFECT_SPEED_TOPIC",
                      "roll_speed"      : "MQTT_EFFECT_SPEED_TOPIC",
                      "blur"            : "MQTT_EFFECT_BLUR_TOPIC",
                      "decay"           : "MQTT_EFFECT_DECAY_TOPIC",
                      "width"           : "MQTT_EFFECT_WIDTH_TOPIC",
                      "mirror"          : "MQTT_EFFECT_MIRROR_TOPIC",
                      "sensitivity"     : "MQTT_EFFECT_SENSITIVITY_TOPIC",
                      "r_multiplier"    : "MQTT_EFFECT_R_TOPIC",
                      "g_multiplier"    : "MQTT_EFFECT_G_TOPIC",
                      "b_multiplier"    : "MQTT_EFFECT_B_TOPIC",
                      "r"               : "MQTT_EFFECT_R_TOPIC",
                      "g"               : "MQTT_EFFECT_G_TOPIC",
                      "b"               : "MQTT_EFFECT_B_TOPIC",
                      "gamma_r"         : "MQTT_EFFECT_R_TOPIC",
                      "gamma_g"         : "MQTT_EFFECT_G_TOPIC",
                      "gamma_b"         : "MQTT_EFFECT_B_TOPIC",
                      "color_mode"      : "MQTT_EFFECT_PALETTE_TOPIC",
                      "color"           : "MQTT_EFFECT_COLOR_TOPIC",
                      "flash_color"     : "MQTT_EFFECT_COLOR_FLASH_TOPIC",
                      "color_mode"      : "MQTT_EFFECT_PALETTE_TOPIC",
                      "lows_color"      : "MQTT_EFFECT_COLOR_LOWS_TOPIC",
                      "mids_color"      : "MQTT_EFFECT_COLOR_MIDS_TOPIC",
                      "high_color"      : "MQTT_EFFECT_COLOR_HIGH_TOPIC",
                      "capturefps"      : "MQTT_EFFECT_CAPTURE_FPS_TOPIC",
                      "contrast"        : "MQTT_EFFECT_CONTRAST_TOPIC",
                      "saturation"      : "MQTT_EFFECT_SATURATION_TOPIC",
                      "bias_min"        : "MQTT_EFFECT_MIN_LEVEL_TOPIC",
                      "reverse"         : "MQTT_EFFECT_REVERSE_TOPIC",
                      "flip_lr"         : "MQTT_EFFECT_FLIP_LR_TOPIC",
                      "quality"         : "MQTT_EFFECT_QUALITY_TOPIC",
                      },
    
    #mapping of setting to scale
    "setting_scales":{"current_effect"  : None,
                      "MIN_FREQUENCY"   : 1,
                      "MAX_FREQUENCY"   : 1,
                      "speed"           : 1000,
                      "roll_speed"      : 1000,
                      "blur"            : 1000,
                      "decay"           : 1000,
                      "width"           : 1,
                      "mirror"          : 1,
                      "sensitivity"     : 1000,
                      "r_multiplier"    : 1000,
                      "g_multiplier"    : 1000,
                      "b_multiplier"    : 1000,
                      "r"               : 1000.0 / 255.0,
                      "g"               : 1000.0 / 255.0,
                      "b"               : 1000.0 / 255.0,
                      "gamma_r"         : 1000 / 5,
                      "gamma_g"         : 1000 / 5,
                      "gamma_b"         : 1000 / 5,
                      "color_mode"      : None,
                      "color"           : None,
                      "flash_color"     : None,
                      "color_mode"      : None,
                      "lows_color"      : None,
                      "mids_color"      : None,
                      "high_color"      : None,
                      "capturefps"      : 1,
                      "contrast"        : 1000,
                      "saturation"      : 1000,
                      "bias_min"        : 1,
                      "reverse"         : 1,
                      "flip_lr"         : 1,
                      "quality"         : None,
                      }

}


device_req_config = {"Stripless"   : None, # duh
                     "BlinkStick"  : None,
                     "DotStar"     : None,
                     "ESP8266"     : {"AUTO_DETECT": ["Auto Detect",
                                                      "Automatically detect device on network using MAC address",
                                                      "checkbox",
                                                      True],
                                      "MAC_ADDR"   : ["Mac Address",
                                                      "Hardware address of device, used for auto-detection",
                                                      "textbox",
                                                      "aa-bb-cc-dd-ee-ff"],
                                      "UDP_IP"     : ["IP Address",
                                                      "IP address of device, used if auto-detection isn't active",
                                                      "textbox",
                                                      "xxx.xxx.xxx.xxx"],
                                      "UDP_PORT"   : ["Port",
                                                      "Port used to communicate with device",
                                                      "textbox",
                                                      "7777"]},
                     "RaspberryPi" : {"LED_PIN"    : ["LED Pin",
                                                      "GPIO pin connected to the LED strip RaspberryPi (must support PWM)",
                                                      "textbox",
                                                      "10"],
                                      "LED_FREQ_HZ": ["LED Frequency",
                                                      "LED signal frequency in Hz",
                                                      "textbox",
                                                      "800000"],
                                      "LED_DMA"    : ["DMA Channel",
                                                      "DMA channel used for generating PWM signal",
                                                      "textbox",
                                                      "5"],
                                      "LED_INVERT" : ["Invert LEDs",
                                                      "Set True if using an inverting logic level converter",
                                                      "checkbox",
                                                      True]},
                     "Fadecandy"   : {"SERVER"     : ["Server Address",
                                                      "Address of Fadecandy server",
                                                      "textbox",
                                                      "localhost:7890"]}
                     }

"""
    ~~ NOTES ~~

[use_defaults]

For any dicts in this file (config.py), you can add them into the use_defaults
dict to force the program to use these values over any stored in settings.ini
that you would have set using the GUI. At runtime, settings.ini is used to update
the above dicts with custom set values. 

If you're running a headless RPi, you may want to edit settings in this file, then
specify to use the dict you wrote, rather than have the program overwrite from 
settings.ini at runtime. You could also run the program with the gui, set the 
settings that you want, then disable the gui and the custom settings will still
be loaded. Basically it works as you would expect it to.

[DEVICE TYPE]

Device used to control a single or group of LED strip/s.

Give it a name and the corresponding MQTT setup will control that group.  
Any strips which register to this "device" will also be updated.

So you can have a 1:1 device to strip ratio.  Or have one device control many strips.
If you want to have say 3 devices, which are each attached to 3 strips each, that'll work.

'ESP8266' means that you are using an ESP8266 module to control the LED strip
and commands will be sent to the ESP8266 over WiFi. You can have as many of 
these as your computer is able to handle.

There's been significant changes to this which have only been tested with an ESP8266 chip.

So the below still exist, but I can't guarantee any of them work as I've never made any attempt
to maintain or test them.

'RaspberryPi' means that you are using a Raspberry Pi as a standalone unit to process
audio input and control the LED strip directly.

'BlinkStick' means that a BlinkstickPro is connected to this PC which will be used
to control the leds connected to it.

'Fadecandy' means that a Fadecandy server is running on your computer and is connected
via usb to a Fadecandy board connected to LEDs

'DotStar' creates an APA102-based output device. LMK if you have any success 
getting this to work becuase i have no clue if it will.

'Stripless' means that the program will run without sending data to a strip.
Useful for development etc, but doesn't look half as good ;)

[REQUIRED CONFIGURATION KEYS]

===== 'ESP8266'
 "AUTO_DETECT"            # Set this true if you're using windows hotspot to connect (see below for more info)
 "MAC_ADDR"               # MAC address of the ESP8266. Only used if AUTO_DETECT is True
 "UDP_IP"                 # IP address of the ESP8266. Must match IP in ws2812_controller.ino
 "UDP_PORT"               # Port number used for socket communication between Python and ESP8266
===== 'RaspberryPi'
 "LED_PIN"                # GPIO pin connected to the LED strip pixels (must support PWM)
 "LED_FREQ_HZ"            # LED signal frequency in Hz (usually 800kHz)
 "LED_DMA"                # DMA channel used for generating PWM signal (try 5)
 "BRIGHTNESS"             # Brightness of LED strip between 0 and 255
 "LED_INVERT"             # Set True if using an inverting logic level converter
===== 'BlinkStick'
 No required configuration keys
===== 'Fadecandy'
 "SERVER"                 # Address of Fadecandy server. (usually 'localhost:7890')
===== 'DotStar'
 No required configuration keys
===== 'Stripless'
 No required configuration keys (heh)

[AUTO_DETECT]

Set to true if the ip address of the device changes. This is the case if it's connecting
through windows hotspot, for instance. If so, give the mac address of the device. This 
allows windows to look for the device's IP using "arp -a" and finding the matching
mac address. I haven't tested this on Linux or macOS.

[FPS]

FPS indicates the desired refresh rate, or frames-per-second, of the audio
visualization. The actual refresh rate may be lower if the computer cannot keep
up with desired FPS value.

Higher framerates improve "responsiveness" and reduce the latency of the
visualization but are more computationally expensive.

Low framerates are less computationally expensive, but the visualization may
appear "sluggish" or out of sync with the audio being played if it is too low.

The FPS should not exceed the maximum refresh rate of the LED strip, which
depends on how long the LED strip is.

[N_FFT_BINS]

Fast Fourier transforms are used to transform time-domain audio data to the
frequency domain. The frequencies present in the audio signal are assigned
to their respective frequency bins. This value indicates the number of
frequency bins to use.

A small number of bins reduces the frequency resolution of the visualization
but improves amplitude resolution. The opposite is true when using a large
number of bins. More bins is not always better!

There is no point using more bins than there are pixels on the LED strip.
"""

for board in settings["devices"]:
    if settings["devices"][board]["configuration"]["TYPE"] == 'ESP8266':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = False
        # Set to False because the firmware handles gamma correction + dither
    elif settings["devices"][board]["configuration"]["TYPE"] == 'RaspberryPi':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = True
        # Set to True because Raspberry Pi doesn't use hardware dithering
    elif settings["devices"][board]["configuration"]["TYPE"] == 'BlinkStick':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = True
    elif settings["devices"][board]["configuration"]["TYPE"] == 'DotStar':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = False
    elif settings["devices"][board]["configuration"]["TYPE"] == 'Fadecandy':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = False
    elif settings["devices"][board]["configuration"]["TYPE"] == 'Stripless':
        settings["devices"][board]["configuration"]["SOFTWARE_GAMMA_CORRECTION"] = False
    else:
        raise ValueError("Invalid device selected. Device {} not known.".format(settings["devices"][board]["configuration"]["TYPE"]))
    settings["devices"][board]["effect_opts"]["Power"]["s_count"] =  settings["devices"][board]["configuration"]["N_PIXELS"]//6
    # Cheeky lil fix in case the user sets an odd number of LEDs
    if settings["devices"][board]["configuration"]["N_PIXELS"] % 2:
        settings["devices"][board]["configuration"]["N_PIXELS"] -= 1

# Ignore these
# settings["configuration"]['_max_led_FPS'] = int(((settings["configuration"]["N_PIXELS"] * 30e-6) + 50e-6)**-1.0)

