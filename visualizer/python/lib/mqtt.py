import paho.mqtt.client as mqtt
import time
import numpy as np
import lib.config as config
import lib.microphone as microphone
import lib.devices as devices
from lib.config import log

if config.settings["configuration"]["USE_LIFX"]:
  from lifxlan import LifxLAN, Light, Group, RGBtoHSBK
  

boards = {}

## Because multiple systems are calling commands and setting status here (which then update ui, which may also call commands and set status),
## there can be feedback loops where the cmnd and status messages get out of sync causing ping-ponging between two values.
## This debouncer will ignore a message if it bounced back and forth quickly, making it rest on one state or the other
debouncer = {}
def debounce_message( message ):
  #log( "debouncer received : " + str( message.topic ) )
  payload = str(message.payload.decode("utf-8"))
  if message.topic in debouncer:
    prev_time = debouncer[message.topic][0]
    prev_payload = debouncer[message.topic][1]
    
    if time.time() - prev_time < 0.5:
      if payload == prev_payload:
        log( ("Debounce Event Detected : " + message.topic +" "+ payload ), 5 )
        return True
      else:
        #log( ("Not Debouncing : " + message.topic +" "+ payload + " Prev : " + prev_payload ), 2 )
        return False

  debouncer[message.topic] = ( time.time(), payload )
  #log ( ("Updating Debounce : " + message.topic +" "+ payload ), 2 )
  #log( "debouncer : " + str( debouncer ) )
  return False
    
    
def on_message(client, userdata, message):
  log(message.topic+" "+str(message.qos)+" "+str(message.payload))
  
def on_message_light_array_ip(client, userdata, message):
  # Add Requesting Lights into our UDP Array of IPs
  # Strip off the parts we don't need and grab the bits we do
  # stat/visualizer/[boardname]/lights/[name]/ip
  while userdata:
    pass
  userdata = 1
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_STAT_PREFIX"], "" )
  entries = msg.split("/", 4)
  board = entries[0]
  stripname = entries[2]
  ip =str(message.payload.decode("utf-8"))
  if ip is "" or ip is None:
    log ( "Removed " + stripname )
    return
  log( "Received Message for " + board + " " + stripname + " IP : " + ip )
  
  if board in config.settings["devices"]:
    if stripname in config.settings["devices"][board]["configuration"]["light_array"]:
      ip =str(message.payload.decode("utf-8"))
      log( "Changing " + stripname + " ip to :" + ip )
      config.settings["devices"][board]["configuration"]["light_array"][stripname]["ip"] = ip
    else:
      new_light_array = { stripname:{ "ip":ip, "state":config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_AVAILABLE"]} }
      current_light_array = config.settings["devices"][board]["configuration"]["light_array"]
      config.settings["devices"][board]["configuration"]["light_array"] = {**current_light_array, **new_light_array}
      log ( "New LED Strip added : " )
      log ( new_light_array )
      # + config.settings["devices"][board]["configuration"]["light_array"] )
      mqtt_topic = config.settings["MQTT"]["MQTT_STAT_PREFIX"] + board + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + stripname + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_TOPIC"]
      #log( mqtt_topic )
      #log( config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_AVAILABLE"] )
      client.publish( mqtt_topic, config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_AVAILABLE"] )
      
      update_mqtt_setting_status( client )
  else:
    log( "ERROR: No Board By the name : " + board )
  userdata = 0

def on_message_light_array_state(client, userdata, message):
  #mutex
  while userdata:
    pass
  userdata = 1
  # Strip off the parts we don't need and grab the bits we do
  # stat/visualizer/[boardname]/lights/[name]/ip
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  entries = msg.split("/", 4)
  board = entries[0]
  stripname = entries[2]
  availability = str(message.payload.decode("utf-8"))
  log( "Received Message for " + board + " " + stripname + " State : " + availability )
  
  if board in config.settings["devices"]:
    if stripname in config.settings["devices"][board]["configuration"]["light_array"]:
      ip =str(message.payload.decode("utf-8"))
      log( "Changing " + stripname + " state to :" + availability )
      config.settings["devices"][board]["configuration"]["light_array"][stripname]["state"] = availability
      if availability == config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_UNAVAILABLE"]:
        log( 'Disabling LED Strip ' + stripname + ' and Removing IP ' + config.settings["devices"][board]["configuration"]["light_array"][stripname]["ip"] + ' from Array ' )
        #log( config.settings["devices"][board]["configuration"]["light_array"] )
        current_light_array = config.settings["devices"][board]["configuration"]["light_array"]
        deleted_light_array = { stripname:{ "ip":current_light_array[stripname]["ip"], "state":config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_PAYLOAD_UNAVAILABLE"]} }
        #send this command to only the one we want to delete.  I'm sure there's some smarter way to access the specific one directly, but whatev
        config.settings["devices"][board]["configuration"]["light_array"] = deleted_light_array
        #log( config.settings["devices"][board]["configuration"]["light_array"] ) 
        pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
        pixels[0][0] = 10;
        boards[board].show(pixels)
        del current_light_array[stripname]
        config.settings["devices"][board]["configuration"]["light_array"] = current_light_array
        # We have to do some funky stuff around the ip/state topics because at the point a light jumps on, 
        # it loses it's MQTT connection to switch to UDP.  We retain the IP so we can survive the visualizer being restarted,
        # but we want to kill the retained ip if the strip is disabled externally
        mqtt_unretain_topic = config.settings["MQTT"]["MQTT_STAT_PREFIX"] + board + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + stripname + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_IP_TOPIC"]
        client.publish( mqtt_unretain_topic, None, True )
        #log( config.settings["devices"][board]["configuration"]["light_array"] )
      client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
    else:
      log( "Received State Setting for as-yet unregistered LED Strip!" )
  else:
    log( "ERROR: No Board By the name : " + board )
  #mutex
  userdata = 0

def audio_enabled():
  global enabled
  return enabled
  
def on_message_audio_enable(client, userdata, message):
  if not config.settings["configuration"]["USE_MQTT"]:
    return True
  global enabled
  global last_audio_enable_msg
  update_mqtt_setting_status( client )
  last_audio_enable_msg = 0
  audio_enable = min( 1, max( -1, int(message.payload.decode("utf-8"))))
  log('Audio Mode Value Received :' + str( audio_enable ) )
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
  if ( audio_enable is not -1 ):
    enabled = audio_enable == 1
    pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
    pixels[0][0] = audio_enable + 10;
    for board in boards:
      boards[board].show(pixels)


def on_message_audio_effect(client, userdata, message):
  if debounce_message( message ):
    return
  # cmnd/visualizer/[boardname]/effect/[effectsetting]
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  entries = msg.split("/", 4)
  board = entries[0]
  topic = entries[2]
  eff = config.settings["devices"][board]["configuration"]["current_effect"]
  if config.settings["MQTT"]["MQTT_EFFECT_MODE_TOPIC"] == topic:
    # a bit of special handling for the effect mode...
    if str(message.payload.decode("utf-8") ) in config.settings["devices"][board]["effect_opts"]:
      config.settings["devices"][board]["configuration"]["current_effect"] = str(message.payload.decode("utf-8") )
      log( 'Setting Effect Mode From MQTT : ' + str(message.payload.decode("utf-8") ))
    else:
      log('Effect Mode Not Found : ' + str(message.payload.decode("utf-8") ))
  else:
    for setting in config.settings["setting_topics"]:
      if config.settings["MQTT"][config.settings["setting_topics"][setting]] == topic:
        if setting in config.settings["devices"][board]["effect_opts"][eff]:
          log('Effect Value Received : ' + setting + " - " + str(message.payload.decode("utf-8")), 6 )
          if config.settings["setting_scales"][setting] is not None:
            value = round( int( message.payload.decode("utf-8") ) * float ( 1.0 / config.settings["setting_scales"][setting] ) , 3 ) 
          else:
            value = str( message.payload.decode("utf-8") )
          config.settings["devices"][board]["effect_opts"][eff][setting] = value
          client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
          if config.settings["configuration"]["USE_GUI"] and 'gui' in globals():
            gui.update_ui_option( eff, setting, value ) 

  
def on_message_audio_effect_frequency_min(client, userdata, message):
  log('Effect Frequency Min Value Received : ' + str(int(message.payload.decode("utf-8"))) )
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  entries = msg.split("/", 4)
  board = entries[0]
  config.settings["devices"][board]["configuration"]["MIN_FREQUENCY"] = int(message.payload.decode("utf-8"))
  client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
  if config.settings["configuration"]["USE_GUI"] and 'gui' in globals():
    gui.board_tabs_widgets[board]["freq_slider"].setRange(config.settings["devices"][board]["configuration"]["MIN_FREQUENCY"], config.settings["devices"][board]["configuration"]["MAX_FREQUENCY"])
  
def on_message_audio_effect_frequency_max(client, userdata, message):
  log('Effect Frequency Max Value Received : ' + str(int(message.payload.decode("utf-8"))) )
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  entries = msg.split("/", 4)
  board = entries[0]
  config.settings["devices"][board]["configuration"]["MAX_FREQUENCY"] = int(message.payload.decode("utf-8"))
  client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
  if config.settings["configuration"]["USE_GUI"] and 'gui' in globals():
    gui.board_tabs_widgets[board]["freq_slider"].setRange(config.settings["devices"][board]["configuration"]["MIN_FREQUENCY"], config.settings["devices"][board]["configuration"]["MAX_FREQUENCY"])
  
  
def on_message_audio_dimmer(client, userdata, message):
  if debounce_message( message ):
    return
  dimmer_value = min( 100, max( -1, int(message.payload.decode("utf-8"))))
  log('Dimmer Value Received :' + str( dimmer_value ) )
  if ( dimmer_value is not -1 ):
    pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
    pixels[1][0] = dimmer_value + 100
    for board in boards:
      boards[board].show(pixels)
    msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
    client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )

def on_message_audio_debug(client, userdata, message):
  debug_value = min( 255, max( -1, int(message.payload.decode("utf-8"))))
  log('Debug Value Received :' + str( debug_value ) )
  if ( debug_value is not -1 ):
    pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
    pixels[2][0] = debug_value
    for board in boards:
      boards[board].show(pixels)
  
def on_message_audio_power(client, userdata, message):
  power_value = message.payload.decode("utf-8")
  log('Power Value Received :' + str( power_value ) )
  if str( power_value ) == 'on':
    power_value = 1
  if str( power_value ) == 'off':
    power_value = 0
  if str( power_value ) == 'sleep':
    power_value = 0
  power_value = min( 1, max( -1, int(power_value)))
  if ( power_value is not -1 ):
    pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
    pixels[0][0] = power_value + 20;
    for board in boards:
      boards[board].show(pixels)
    msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
    client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
        

def on_message_audio_scheme(client, userdata, message):
  scheme_value = min( 12, max( -1, int(message.payload.decode("utf-8"))))
  log('Scheme Value Received : ' + str( scheme_value ) )
  if ( scheme_value is not -1 ):
    pixels = np.array([[0 for i in range( 1 )] for i in range(3)])
    pixels[0][0] = scheme_value + 30;
    for board in boards:
      boards[board].show(pixels)
      
def on_message_audio_device(client, userdata, message):
  log('Audio Device Select Received : ' + str(message.payload.decode("utf-8")) )
  msg = message.topic.replace( config.settings["MQTT"]["MQTT_CMND_PREFIX"], "" )
  config.settings["configuration"]["MIC_NAME"] = str( message.payload.decode("utf-8") )
  client.publish( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + msg, message.payload )
  microphone.reset_microphone_device()

def update_input_select_lists( client ):
  # We'll use retain here so the lists survive home assistant restarts
  for board in config.settings["devices"]:
    MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( board ) )
    
    audio_devices = microphone.get_audio_devices()
    log( "Adding Audio Device Options  : " + str( audio_devices ), 4 )
    client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_AUDIO_DEVICES_TOPIC"], audio_devices, 1, True )
    
    gradients = ''
    for gradient in config.settings["gradients"]:
      if gradients != '':
        gradients += ','
      gradients += gradient
    log( "Adding Palette Options  : " + str( gradients ), 4 )
    client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_PALETTE_OPTIONS_TOPIC"], gradients, 1, True )
    
    color_list = ''
    for color in config.settings["colors"]:
      if color_list != '':
        color_list += ','    
      color_list += color
    log( "Adding Color Options  : " + str( color_list ), 4 )
    client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_COLOR_OPTIONS_TOPIC"], color_list, 1, True )

    effect_list = ''
    for effect in config.settings["devices"][board]["effect_opts"]:
      if effect_list != '':
        effect_list += ','    
      effect_list += effect
    log( "Adding Effect Options  : " + str( effect_list ), 4 )
    client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_EFFECT_OPTIONS_TOPIC"], effect_list, 1, True )
      
def update_effect_setting( client, board, setting ):
    if not config.settings["configuration"]["USE_MQTT"]:
        return
    MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( board ) )
    effect = config.settings["devices"][board]["configuration"]["current_effect"]
    if setting in config.settings["devices"][board]["effect_opts"][effect] and setting in config.settings["setting_topics"]:
      topic = config.settings["setting_topics"][setting]
      scalar = config.settings["setting_scales"][setting]
      value = config.settings["devices"][board]["effect_opts"][effect][setting]
      if scalar is not None:
        value = int( value * scalar )
      client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"][topic], value )
      
def update_config_setting( client, board, setting ):
    if not config.settings["configuration"]["USE_MQTT"]:
        return
    MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( board ) )
    if setting in config.settings["devices"][board]["configuration"] and setting in config.settings["setting_topics"]:
      topic = config.settings["setting_topics"][setting]
      scalar = config.settings["setting_scales"][setting]
      value = config.settings["devices"][board]["configuration"][setting]
      if scalar is not None:
        value = int( value * scalar )
      client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"][topic], value )

def update_mqtt_setting_status( client ):
  if not config.settings["configuration"]["USE_MQTT"]:
    return
  for board in config.settings["devices"]:
    log( "Updating MQTT Settings for current mode", 6 )
    update_config_setting( client, board, "current_effect" )
    update_config_setting( client, board, "MIN_FREQUENCY" )
    update_config_setting( client, board, "MAX_FREQUENCY" )
    
    update_effect_setting( client, board, "speed" )
    update_effect_setting( client, board, "roll_speed" )
    update_effect_setting( client, board, "blur" )
    update_effect_setting( client, board, "decay" )
    update_effect_setting( client, board, "width" )
    update_effect_setting( client, board, "mirror" )
    update_effect_setting( client, board, "sensitivity" )
    update_effect_setting( client, board, "r_multiplier" )
    update_effect_setting( client, board, "g_multiplier" )
    update_effect_setting( client, board, "b_multiplier" )
    update_effect_setting( client, board, "r" )
    update_effect_setting( client, board, "g" )
    update_effect_setting( client, board, "b" )
    update_effect_setting( client, board, "gamma_r" )
    update_effect_setting( client, board, "gamma_g" )
    update_effect_setting( client, board, "gamma_b" )
    update_effect_setting( client, board, "color_mode" )
    update_effect_setting( client, board, "color" )
    update_effect_setting( client, board, "flash_color" )
    update_effect_setting( client, board, "color_mode" )
    update_effect_setting( client, board, "reverse" )
    update_effect_setting( client, board, "flip_lr" )
    update_effect_setting( client, board, "lows_color" )
    update_effect_setting( client, board, "mids_color" )
    update_effect_setting( client, board, "high_color" )
    update_effect_setting( client, board, "saturation" )
    update_effect_setting( client, board, "contrast" )
    update_effect_setting( client, board, "capturefps" )
    update_effect_setting( client, board, "quality" )
    
def format_color_rgb_hex( color ):
    return f'#{int(round(color[0])):02x}{int(round(color[1])):02x}{int(round(color[2])):02x}'
    
def update_zone( client, board, topic, value ):
    if not config.settings["configuration"]["USE_MQTT"]:
        return
    MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( board ) + config.settings["MQTT"]["MQTT_ZONE_BASE_TOPIC"])
    client.publish(MQTT_STAT_Prefix + topic, format_color_rgb_hex( value ) )
    
def update_zones( client, self ):
    if config.settings["configuration"]["USE_MQTT"]:
      MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( self.board ) + config.settings["MQTT"]["MQTT_ZONE_BASE_TOPIC"])
      output = format_color_rgb_hex( self.zone_avg_total )
      if update_zones.total != output:
        update_zones.total = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_GLOBAL_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_GLOBAL_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_GLOBAL_CUSTOM_TOPIC"], output )
      output = format_color_rgb_hex( self.zone_avg_center )
      if update_zones.center != output:
        update_zones.center = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_CENTER_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_CENTER_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_CENTER_CUSTOM_TOPIC"], output )
      output = format_color_rgb_hex( self.zone_avg_top )
      if update_zones.top != output:
        update_zones.top = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_TOP_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_TOP_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_TOP_CUSTOM_TOPIC"], output )      
      output = format_color_rgb_hex( self.zone_avg_right )
      if update_zones.right != output:
        update_zones.right = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_RIGHT_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_RIGHT_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_RIGHT_CUSTOM_TOPIC"], output )
      output = format_color_rgb_hex( self.zone_avg_bot )
      if update_zones.bot != output:
        update_zones.bot = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_BOT_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_BOT_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_BOT_CUSTOM_TOPIC"], output ) 
      output = format_color_rgb_hex( self.zone_avg_left )
      if update_zones.left != output:
        update_zones.left = output
        client.publish(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_ZONE_LEFT_TOPIC"], output )
        if config.settings["MQTT"]["MQTT_ZONE_LEFT_CUSTOM_TOPIC"] is not None:
            client.publish( config.settings["MQTT"]["MQTT_ZONE_LEFT_CUSTOM_TOPIC"], output ) 
      
          
def assign_light_group( lifx, group, singles ):
  lights = []
  if singles is not None:
    for light in singles:
      if type(light) is list:
        lights.append( Light( light[0], light[1] ) )
      else:
        lights.append( lifx.get_devices_by_name( light ).get_device_list() )
  if group is not None:
    lights = lights + lifx.get_devices_by_group( group ).get_device_list()
  return Group( lights )
        
def initialize_mqtt( mainboards ):
    if not config.settings["configuration"]["USE_MQTT"]:
        return
    global boards
    log( 'Initializing MQTT', 2 )
    mqtt_mutex = 0
    boards = mainboards
    client = mqtt.Client( userdata=mqtt_mutex )
    #client.max_inflight_messages_set(16)
    client.connect( config.settings["configuration"]["MQTT_IP"], config.settings["configuration"]["MQTT_PORT"], 60)
    client.loop_start()
    

    if config.settings["configuration"]["USE_LIFX"]:
      update_zones.lifx = LifxLAN( config.settings["LiFX"]["LIFX_NUMLIGHTS"] )

      # get devices
      if config.settings["LiFX"]["LIFX_DISCOVER_LIGHTS"]:
        log( "LiFX Discovery..." )
        devices = update_zones.lifx.get_lights()

        log("Found Bulbs:")
        for device in devices:
          log( str( device.get_label() ) + ' - Add directly as :  ["' + str( device.get_mac_addr() ) + '", "' + str( device.get_ip_addr() ) + '"]' )
            
      update_zones.group_global = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_GLOBAL_GROUP"], config.settings["LiFX"]["LIFX_GLOBAL_LIGHTS"] )
      update_zones.group_center = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_CENTER_GROUP"], config.settings["LiFX"]["LIFX_CENTER_LIGHTS"] )
      update_zones.group_top = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_TOP_GROUP"], config.settings["LiFX"]["LIFX_TOP_LIGHTS"] )
      update_zones.group_right = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_RIGHT_GROUP"], config.settings["LiFX"]["LIFX_RIGHT_LIGHTS"] )
      update_zones.group_bot = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_BOT_GROUP"], config.settings["LiFX"]["LIFX_BOT_LIGHTS"] )
      update_zones.group_left = assign_light_group( update_zones.lifx, config.settings["LiFX"]["LIFX_LEFT_GROUP"], config.settings["LiFX"]["LIFX_LEFT_LIGHTS"] )

    update_zones.total = 0
    update_zones.center = 0
    update_zones.top = 0
    update_zones.right = 0
    update_zones.bot = 0
    update_zones.left = 0
    
    log ( 'Per Board Initialization' )
    for board in config.settings["devices"]:
      log( "Initializing Board " + str( board ), 2 )
      MQTT_CMND_Prefix = ( config.settings["MQTT"]["MQTT_CMND_PREFIX"] + str( board ) )
      MQTT_STAT_Prefix = ( config.settings["MQTT"]["MQTT_STAT_PREFIX"] + str( board ) )

      client.on_message = on_message
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + "+", on_message_audio_effect)
      log('Subscribing To Effects Topics : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + "+", 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + "+", 2 )

      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_ENABLE_TOPIC"], on_message_audio_enable)
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DIMMER_TOPIC"], on_message_audio_dimmer)
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DEBUG_TOPIC"], on_message_audio_debug)
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_POWER_TOPIC"], on_message_audio_power)
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_SCHEME_TOPIC"], on_message_audio_scheme)
      
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_MICROPHONE_TOPIC"], on_message_audio_device)

      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MIN_TOPIC"], on_message_audio_effect_frequency_min)
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MAX_TOPIC"], on_message_audio_effect_frequency_max)
      
      client.message_callback_add(MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_IP_TOPIC"], on_message_light_array_ip )
      client.message_callback_add(MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_TOPIC"], on_message_light_array_state )
      

      log('Subscribing To Light Mode : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_ENABLE_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_ENABLE_TOPIC"], 2 )
      log('Subscribing To Dimmer : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DIMMER_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DIMMER_TOPIC"], 2 )
      log('Subscribing To Debug : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DEBUG_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_DEBUG_TOPIC"], 2 )
      log('Subscribing To Power : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_POWER_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_POWER_TOPIC"], 2 )	  
      log('Subscribing To Scheme : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_SCHEME_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_SCHEME_TOPIC"], 2 )	
      log('Subscribing To Frequency Min : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MIN_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MIN_TOPIC"], 2 )
      log('Subscribing To Frequency Max : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MAX_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_EFFECT_BASE_TOPIC"] + config.settings["MQTT"]["MQTT_EFFECT_FREQUENCY_MAX_TOPIC"], 2 )
      
      log('Subscribing To Microphone : ' + MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_MICROPHONE_TOPIC"], 3 )
      client.subscribe( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_MICROPHONE_TOPIC"], 2 )
      
      log('Subscribing To Light Array IP : ' + ( MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_IP_TOPIC"]), 3 )
      client.subscribe( ( MQTT_STAT_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_IP_TOPIC"] ), 2 )
      log('Subscribing To Light Array State : ' + ( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_TOPIC"]), 3 )
      client.subscribe( ( MQTT_CMND_Prefix + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_ARRAY_TOPIC"] + '+' + config.settings["MQTT"]["MQTT_AVAILABLE_LIGHTS_STATE_TOPIC"] ), 2 )
      
      update_input_select_lists( client )
      update_mqtt_setting_status( client )
      
      log( "Board " + str( board ) + " Initialized", 3 )
    
    log( 'All MQTT Initialized', 3 )
    return client
