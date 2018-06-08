## Vela - A Sonoff LED Visualizer
<img src="https://github.com/rando-calrissian/Visualight/blob/development/images/backlight.gif" width="480" align="right" />
<img src="https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/images/description-cropped.gif" width="480" align="right" />


A general ESP8266/Sonoff controller for WS2812/SK6812 LED Strips that has a range of lighting FX but can also be driven externally with both Audio Visualizer and Backlighting features (simple Ambilight/Hyperion functionality).

It has a local GUI as well as an MQTT interface for the visualizer, and a set of controls for Home Assistant as well. 

Multiple LED Strip clients can be driven by the single visualizer.  The visualizer renders for a defined set of virtual pixels which are remapped into the actual number of LED pixels per-strip.  

The Sonoff-Tasmota based firmware for ESP8266 devices allows for a robust general lighting interface that can control audio/video visualizations via an external Python application and Home Assistant integration.

It also supports detecting the display state (monitor or TV) of the machine it is running on to toggle the lights (or drive other automations).

In addition it has zone output for the screen visualization so other point light sources can show the general colors via MQTT or directly to LiFX bulbs.

I just made this for my own entertainment, with a lot of experimentation and learning along the way.  If it's useful to you, great!



## How it works
<img src="https://github.com/rando-calrissian/Visualight/blob/development/images/hass.png" height="500" align="right" />

<img src="https://github.com/rando-calrissian/Visualight/blob/development/images/gui.png" height="500" align="right" />
Generally speaking your light strip works just like you were using an LED Strip with Tasmota normally.  You have Home Assistant options for the brightness and scheme, but you also have a seperate FX Controller.
When the light is put into the External FX mode, it will stop being driven locally and start being driven by the visualizer over a UDP connection.  From here, everything is driven by the FX visualizer.
Strips can be opted in/out of control here, but their normal controls will stop working while opted in.  Music fed in via mic or audio loopback can be visualized, as can the screen border colors of the machine running the visualization.

The visualizer app can have multiple visualizations running simultaneously.  Each of these has their own name and settings.  Each of these "devices" can control as many seperate LED strips running the firmware as you'd like.  So you can always have a strict 1:1 relationship between individual strips and their visualization, or group them all together, or anywhere in between.

## Background
I wanted to add some LED strips to a few places and integrate it into my existing automation solutions.  
I'm a big fan of the Tasmota firmware for Sonoff and ESP8266 devices, so it seemed like a good starting place.  Mostly these were for lighting, but I wanted to be able to have some fun with them too.  Tasmota has pretty limited options for controlling LED Strips, but otherwise it's a solid and versatile setup with a great web interface, MQTT interface, OTA support, etc.  I wanted to keep all of this stuff for my setup if possible.

Most of the other options out there for doing LED FX were great for that, but limited in many other ways.  I decided to take a stab at integrating the two together.

I initially looked at just expanding what was there by directly adding more FX to Tasmota, but I fell down the rabbithole of wanting to do some audio visualization as well.  I stumbled across a nice existing base for this with the [Reactive Audio Strip](https://github.com/scottlawsonbc/audio-reactive-led-strip)/[Systematic-LEDs](https://github.com/not-matt/Systematic-LEDs) work.
I also figured some bias lighting/Ambilight style backlighting effects would be nice to have.  None of the existing solutions here I could find are Windows based and pretty much all of them want you to be running off a raspberry pi (which I'm not).  I decided to try out just doing my own version in the existing python audio visualizer core.  I haven't used python at all prior to this, so my approach is probably naive and certainly less optimal than it could otherwise be, but it works for my purposes.

Could I have just used a raspberry pi here for the strips doing backlighting and ditched the ESP8266?  Sure, but it's fun to have them all be able to sync up for audio and all have the same general functionality including automation.  If a pure backlighting solution more fits your bill, there are options out there.

## Original sources
This stuff is 90% the work of the original authors, I just crammed them all together and added some functionality and features here and there.


[Tasmota Firmware](https://github.com/arendst/Sonoff-Tasmota) by Theo Arends

[Original Audio Reactive LEDs](https://github.com/scottlawsonbc/audio-reactive-led-strip) by Scott Lawson

[Systematic LEDs Fork](https://github.com/not-matt/Systematic-LEDs) by Matthew Bowley

[Screen Capture](https://nicholastsmith.wordpress.com/2017/08/10/poe-ai-part-4-real-time-screen-capture-and-plumbing) by Nicholas T. Smith


## Caveats
This is currently Windows only.  That's what I'm using it on, so that's where all the work has gone.  Mostly it'd work wherever, but the display detection and screengrabbing are Windows specific.  It could go multiplatform with a little bit of work in those areas.

I've seen a problem where it seems like UDP messages get queued and the strip falls behind.  Try lowering your framerate in this scenario.  Mine seemed to happen above 60 regularly.

I found that I couldn't have an active UDP stream going to the ESP8266 for FX while also maintaining the webserver or MQTT connections.  Trying to do so would cause them to fail and leak heap memory until the ESP8266 crashed.
Given that the audio/video effects are realtime, it didn't look like there'd be way to interleave them or anything either. 
So while the audio/video driven FX are live, the web and mqtt interfaces to the strip are disabled.  You have to use the FX side of the controls to drive the strip.  This includes a few non-effect messages that can be sent to the strip to change it out of audio mode, change brightness, etc.

I tried UDP multicast and found that for some reason I got far worse performance.  It went from 60 fps down to ~10-15.  I tried a few solutions here, but I didn't ultimately figure out how to get multicast performance to match unicast.
As such, each strip registers itself with the visualizer and gets its own unicast stream.  If you have a whole ton of strips, you'll probably want to investigate the multicast route, although whatever code that is there isn't hooked up at the moment.

## Future steps
More reactive and non-reactive FX.  
Create a custom component for Home Assistant rather than a collection of inputs and automations.

Investigate higher performance screen grabbing techniques.

Expand Zone Support to audio visualization modes.

## Installation


[Please refer to Tasmota Here for the firmware](https://github.com/arendst/Sonoff-Tasmota)

The included files are set up to work with PlatformIO.  I recommend this, as does the base Sonoff-Tasmota, over the default Arduino IDE. 

[For the LED strips, please refer to these instructions regarding installation](https://github.com/scottlawsonbc/audio-reactive-led-strip)

Note that with my SK6812 strips, I required both DMA (via the RX pin) and overclocking to 160Mhz for a stable error-free experience.  It is set up like this by default for PlatformIO.  If using the Arduino IDE, you will need to select the speed option manually.

[Home Assistant](https://www.home-assistant.io/)

[Anaconda](https://www.anaconda.com/download/) or [Conda](https://conda.io/docs/user-guide/install/index.html)

If you want to use this for a TV/Monitor visualizer, the application needs to run on the hardware driving the display.

The LED Strip layout runs clockwise around (when viewing the display from the front).  Under the hood this starts at the Top-Left corner of the display.  There is an option to offset the start pixel so if you choose to start it from a different location that will work.  Mine starts from the mid point at the bottom of my monitor so that other visualizations 'center' is at the top of the monitor, so that is the default offset with the default pixel count.


## Setup

Install the firmware onto your Sonoff or ESP8266 devices which are wired into a WS2812B or SK6812 LED Strip as normal.  You'll have to make changes to the user_config.h file to set up your wifi and mqtt locations, but you'll also find this new block of options :

```
#define MQTT_VISUALIZER_PREFIX    "visualizer"      // ala "cmnd/visualizer/[device]/lights/[name]/ip" - change this if you want to split out multiple controllers (pc's running the visualizer software)
#define MQTT_LIGHTS_TOPIC         "lights"          // the lights topic for registering strips - leave this alone
#define MQTT_LIGHTS_IP_TOPIC      "ip"              // the ip topic for registering strips - leave this alone
#define MQTT_LIGHTS_STATE_TOPIC   "state"           // the state topic for registering strips - leave this alone
#define MQTT_AUDIO_MODE_TOPIC     "cmnd/audio/mode" // on its way to deprecation?
#define MQTT_LIGHT_FX_TOPIC       "monitor"         // Set this to the visualizer 'device' you want to register to - so each visualizer (noted as visualizer above) can have multiple devices - ie, this topic
#define AUDIO_TIMEOUT             15                // If we don't receive any signal from the visualizer for this long, abort and go back normal operation (restore web server, mqtt)
```

In addition, there are two new options you can set via commands (either via the webserver console or MQTT) :

```
fxdevice [name]  -- this sets the name of the device you want to connect to on the visualizer side - it's the MQTT_LIGHT_FX_TOPIC in user_config.h
fxenable [on/off]  -- this turns control over to the visualizer.  Once on, you'll lose connection to the webserver and mqtt access points and must control things via the visualizer or home assistant
```

The easiest Python setup from scracth is to download Anaconda 3.6 or latest.
Open an Anaconda prompt and enter the following to install everything you'll need :

```
conda create -n visualizer
activate visualizer
conda install numpy scipy pyqtgraph
pip install paho-mqtt pyaudio pillow win32gui pywin32 comtypes
```

The MQTT hierarchy used for the various elements is as follows:

```
cmnd/[visualizer]/[device]/effect/color
cmnd/[visualizer]/[device]/lights/[sonoff_mqtt_name]/state
```

Where the Visualizer element is the specific python application that controls one or more instance device.
Each instance device controls one or more LED strips, which each have their own sonoff name.
Each Instance shares all the effect settings across all strips it owns.
So you can have multiple sonoff strips per instance, multiple instances per visualizer, and multiple visualizers, provided they're all uniquely named.


Pick a name for each seperate device instance you want.  The default is "monitor", as noted in the user_config.h above, in the visualizer config.py, and the home assistant widgets.

Each sonoff will subscribe to a specific device instance as specified in the user_cofig.h noted above, and you may change this in the Sonoff webserver console or via MQTT with this command:

```
fxdevice [name]
```


In the visualizer folder, you'll find the python directory which contains the visualizer program.  Edit the python/lib/config.py file to reflect the name of each "device" visualizer you set above (or left alone as "monitor").  You'll also need to set up your MQTT broker address in the same config.py.  Various other options are available to set here if you want to dig in...

The Home Assistant directory contains configuration entries to control the visualizer.  The mqtt entries should be fixed to reflect both the device name of your visualizer and the name of your sonoff.

Whenever you'd like to run this now or in the future, open an Anaconda Prompt and d to the directory you've installed the python to and run:

```
activate visualizer
cd [my visualizer install directory]
python main.py
```

You can create a shortcut link to go directly here by creating a shortcut to the anaconda prompt and then editing the properties and adding the following :

```
&& activate visualizer && python [PATH TO WHERE YOU INSTALLED]\visualizer\python\main.py
```

The entire shortcut link will look something like :

```
%windir%\System32\cmd.exe “/K” C:\Users\[yourusername]\AppData\Local\Continuum\anaconda3\Scripts\activate.bat C:\Users\[yourusername]\AppData\Local\Continuum\anaconda3 && activate visualizer && python C:[pathtoyourinstall]\Vela\visualizer\python\main.py
```

You can then just click on this to launch the visualizer.

Once the visualizer is running you can start sending the visualization to your LEDs by activating the FX mode on your strip.  This can be done via the Home Assistant toggle switch provided or by sending the following command in the sonoff webserver conole or via MQTT:

```
fxenable on
```

to start accepting input from the visualizer.


The Home Assitant controls can be used to activate or deactive each strip and change settings.


## Zone Support

In addition to the LED Strips you directly control, additional point sources can be coordinated with these effects.  Currently, this is only available for the Visualight bias-light visualization.

There are six zones currently available - Global, Center, Top, Right, Bottom, and Left.  They use a running average of the colors from that area to determine a color for that zone.  Currently MQTT zones update 4 times a second when changing in an effort to avoid a lot of load on MQTT, but this will become a setting.  LiFX is transmitted over UDP and updated at the visualizer speed.

In the Visualizer/python/lib/config.py file, under the MQTT and LiFX sections, you can define where and if you'd like to output these zones.

For MQTT, there are generic zone topics which can be used by Home Assistant or other programs to map the color output into whatever devices you want.  The output is defined as a hex RGB color.  

```
                     "MQTT_ZONE_BASE_TOPIC":            "/zones/",                            # Base topic for zones
                     "MQTT_ZONE_GLOBAL_TOPIC":          "zone_global",                        # General Avg Color 
                     "MQTT_ZONE_CENTER_TOPIC":          "zone_center",                        # Center of the Screen Avg Color 
                     "MQTT_ZONE_TOP_TOPIC":             "zone_top",                           # Top Avg Color
                     "MQTT_ZONE_RIGHT_TOPIC":           "zone_right",                         # Right Avg Color
                     "MQTT_ZONE_BOT_TOPIC":             "zone_bot",                           # Bot Avg Color
                     "MQTT_ZONE_LEFT_TOPIC":            "zone_left",                          # Left Avg Color  
```

The topic/payload output to MQTT for a pure red in the center of the screen will look like :

```
stat/[visualizer]/[device]/zones/zone_center
#FF0000
```

There are also a set of custom MQTT topics that can be used to talk to specific devices with a fully custom path.

```
                     "MQTT_ZONE_GLOBAL_CUSTOM_TOPIC":   None,                                 # This topic is a complete MQTT topic for a custom recipient Example : "cmnd/sonoff_led/color"
                     "MQTT_ZONE_CENTER_CUSTOM_TOPIC":   None,                                 # This topic is a complete MQTT topic for a custom recipient Output in Hex : #FF0000
                     "MQTT_ZONE_TOP_CUSTOM_TOPIC":      None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_RIGHT_CUSTOM_TOPIC":    None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_BOT_CUSTOM_TOPIC":      None,                                 # This topic is a complete MQTT topic for a custom recipient
                     "MQTT_ZONE_LEFT_CUSTOM_TOPIC":     None,                                 # This topic is a complete MQTT topic for a custom recipient
```

So for example, to control another sonoff device that's just a single bulb, not an LED strip (or the entirety of an LED strip), this custom strip topic might look like :

```
                     "MQTT_ZONE_CENTER_CUSTOM_TOPIC":   "cmnd/sonoff_led/color",
```

Like normal zones, when active, this will send the payload of the color in hex, such a #FF0000 for red.

LiFX bulbs are also directly supported as Zones.

In Visualizer/python/lib/config.py lifx section, you'll find the following options :

```
                     "LIFX_DISCOVER_LIGHTS":  False,          # Discover and list available lights - takes some time, directly adding lights by mac/ip is faster
                     "LIFX_NUMLIGHTS":        None,           # If the number of lights is known/specified it'll speed up discovery or None
                     "LIFX_GLOBAL_GROUP":     None,           # Group name for the global light Ex: "Living Room" will trigger discovery
                     "LIFX_CENTER_GROUP":     None,           # Group name for the center light
                     "LIFX_TOP_GROUP":        None,           # Group name for the top light
                     "LIFX_RIGHT_GROUP":      None,           # Group name for the right light
                     "LIFX_BOT_GROUP":        None,           # Group name for the bot light
                     "LIFX_LEFT_GROUP":       None,           # Group name for the left light
                     "LIFX_GLOBAL_LIGHTS":    None,           # List of Lights for the global light Ex: ["left light", "right light"] by name will trigger discovery
                     "LIFX_CENTER_LIGHTS":    None,           # List of Lights for the center light or [["12:34:56:78:9a:bc", "192.168.0.2"]] for direct access
                     "LIFX_TOP_LIGHTS":       None,           # List of Lights for the top light
                     "LIFX_RIGHT_LIGHTS":     None,           # List of Lights for the right light
                     "LIFX_BOT_LIGHTS":       None,           # List of Lights for the bot light
                     "LIFX_LEFT_LIGHTS":      None,           # List of Lights for the left light
```

Discover lights will check your network for LiFX lights and print out a list of them to the log.  This list will also include a block of mac address and ip you can copy and paste to access each light directly.  Discovery takes some time, so it will slow your startup of the visualizer.  However, accessing the lights directly is faster.  If you don't expect your lights IP to change, you can take the address of each light and specify it instead of the name for a faster start.  Even if you have "discovery" turned off, if you address you lights or groups by name, it will force them to be found via discovery, where as using the mac/ip combo directly will be faster.

Specifying the NUMLIGHTS will speed up discovery if you're using it.

The Group set of zones allows a LiFX group to be specified for all lights in that zone to use a color.
The Lights categories allow individual or lists of lights to be added.  These can be the light's name or its mac/ip combo.  You can mix and match these together.

A correctly set up LiFX Group and Lights might look like :

```
"LIFX_GLOBAL_GROUP":  "Living Room",
"LIFX_TOP_LIGHTS":    [["12:34:56:78:9d:ef", "192.168.0.3"]],
"LIFX_RIGHT_LIGHTS":  ["Floor Lamp", ["12:34:56:78:9a:bc", "192.168.0.2"], "Couch Lamp"], 
"LIFX_LEFT_LIGHTS":   ["Overhead Light"],
```


## Additional Info

Below is the default readme for Sonoff-Tasmota.

## Sonoff-Tasmota

Alternative firmware for _ESP8266 based devices_ like [iTead](https://www.itead.cc/) _**Sonoff**_ with **web**, **timers**, 'Over The Air' (**OTA**) firmware updates and **sensors support**, allowing control under **Serial**, **HTTP**, **MQTT** and **KNX**, so as to be used on **Smart Home Systems**. Written for Arduino IDE and PlatformIO.

[![GitHub version](https://img.shields.io/github/release/arendst/Sonoff-Tasmota.svg)](https://github.com/arendst/Sonoff-Tasmota/releases/latest)
[![GitHub download](https://img.shields.io/github/downloads/arendst/Sonoff-Tasmota/total.svg)](https://github.com/arendst/Sonoff-Tasmota/releases/latest)
[![License](https://img.shields.io/github/license/arendst/Sonoff-Tasmota.svg)](https://github.com/arendst/Sonoff-Tasmota/blob/development/LICENSE.txt)

If you like **Sonoff-Tasmota**, give it a star, or fork it and contribute!
[![GitHub stars](https://img.shields.io/github/stars/arendst/Sonoff-Tasmota.svg?style=social&label=Star)](https://github.com/arendst/Sonoff-Tasmota/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/arendst/Sonoff-Tasmota.svg?style=social&label=Fork)](https://github.com/arendst/Sonoff-Tasmota/network)

### Development
[![Build Status](https://img.shields.io/travis/arendst/Sonoff-Tasmota.svg)](https://travis-ci.org/arendst/Sonoff-Tasmota)

Current version is **5.14.0a** - See [sonoff/_releasenotes.ino](https://github.com/arendst/Sonoff-Tasmota/blob/development/sonoff/_releasenotes.ino) for change information.

### Quick install
Download one of the released binaries from https://github.com/arendst/Sonoff-Tasmota/releases and flash it to your hardware as documented in the wiki.

### Important User Compilation Information
If you want to compile Sonoff-Tasmota yourself keep in mind the following:

- Only Flash Mode **DOUT** is supported. Do not use Flash Mode DIO / QIO / QOUT as it might seem to brick your device. See [Wiki](https://github.com/arendst/Sonoff-Tasmota/wiki/Theo's-Tasmota-Tips) for background information.
- Sonoff-Tasmota uses a 1M linker script WITHOUT spiffs for optimal code space. If you compile using ESP/Arduino library 2.3.0 then download the provided new linker script to your Arduino IDE or Platformio base folder. Later version of ESP/Arduino library already contain the correct linker script. See [Wiki > Prerequisite](https://github.com/arendst/Sonoff-Tasmota/wiki/Prerequisite).
- To make compile time changes to Sonoff-Tasmota it can use the ``user_config_override.h`` file. It assures keeping your settings when you download and compile a new version. To use ``user_config.override.h`` you will have to make a copy of the provided ``user_config.override_sample.h`` file and add your setting overrides. To enable the override file you will need to use a compile define as documented in the ``user_config_override_sample.h`` file.

### Version Information
- Sonoff-Tasmota provides all (Sonoff) modules in one file and starts with module Sonoff Basic.
- Once uploaded select module using the configuration webpage or the commands ```Modules``` and ```Module```.
- After reboot select config menu again or use commands ```GPIOs``` and ```GPIO``` to change GPIO with desired sensor.

<img src="https://github.com/arendst/arendst.github.io/blob/master/media/sonoffbasic.jpg" width="250" align="right" />

See [Wiki](https://github.com/arendst/Sonoff-Tasmota/wiki) for more information.<br />
See [Community](https://groups.google.com/d/forum/sonoffusers) for forum and more user experience.

The following devices are supported:
- [iTead Sonoff Basic](https://www.itead.cc/smart-home/sonoff-wifi-wireless-switch-1.html)
- [iTead Sonoff RF](https://www.itead.cc/smart-home/sonoff-rf.html)
- [iTead Sonoff SV](https://www.itead.cc/smart-home/sonoff-sv.html)<img src="https://github.com/arendst/arendst.github.io/blob/master/media/sonoff_th.jpg" width="250" align="right" />
- [iTead Sonoff TH10/TH16 with temperature sensor](https://www.itead.cc/smart-home/sonoff-th.html)
- [iTead Sonoff Dual (R2)](https://www.itead.cc/smart-home/sonoff-dual.html)
- [iTead Sonoff Pow with Energy Monitoring](https://www.itead.cc/smart-home/sonoff-pow.html)
- [iTead Sonoff Pow R2 with Energy Monitoring](https://www.itead.cc/sonoff-pow-r2.html)
- [iTead Sonoff 4CH (R2)](https://www.itead.cc/smart-home/sonoff-4ch.html)
- [iTead Sonoff 4CH Pro (R2)](https://www.itead.cc/smart-home/sonoff-4ch-pro.html)
- [iTead S20 Smart Socket](https://www.itead.cc/smart-socket.html)
- [Sonoff S22 Smart Socket](https://github.com/arendst/Sonoff-Tasmota/issues/627)
- [iTead Sonoff S31 Smart Socket with Energy Monitoring](https://www.itead.cc/sonoff-s31.html)
- [iTead Slampher](https://www.itead.cc/slampher.html)
- [iTead Sonoff Touch](https://www.itead.cc/sonoff-touch.html)
- [iTead Sonoff T1](https://www.itead.cc/sonoff-t1.html)
- [iTead Sonoff SC](https://www.itead.cc/sonoff-sc.html)
- [iTead Sonoff Led](https://www.itead.cc/sonoff-led.html)<img src="https://github.com/arendst/arendst.github.io/blob/master/media/sonoff4chpror2.jpg" height="250" align="right" />
- [iTead Sonoff BN-SZ01 Ceiling Led](https://www.itead.cc/bn-sz01.html)
- [iTead Sonoff B1](https://www.itead.cc/sonoff-b1.html)
- [iTead Sonoff RF Bridge 433](https://www.itead.cc/sonoff-rf-bridge-433.html)
- [iTead Sonoff Dev](https://www.itead.cc/sonoff-dev.html)
- [iTead 1 Channel Switch 5V / 12V](https://www.itead.cc/smart-home/inching-self-locking-wifi-wireless-switch.html)
- [iTead Motor Clockwise/Anticlockwise](https://www.itead.cc/smart-home/motor-reversing-wifi-wireless-switch.html)
- [Electrodragon IoT Relay Board](http://www.electrodragon.com/product/wifi-iot-relay-board-based-esp8266/)
- AI Light or any my9291 compatible RGBW LED bulb
- H801 PWM LED controller
- [MagicHome PWM LED controller](https://github.com/arendst/Sonoff-Tasmota/wiki/MagicHome-LED-strip-controller)
- AriLux AL-LC01, AL-LC06 and AL-LC11 PWM LED controller
- [Supla device - Espablo-inCan mod. for electrical Installation box](https://forum.supla.org/viewtopic.php?f=33&t=2188)
- [Luani HVIO board](https://luani.de/projekte/esp8266-hvio/)
- Wemos D1 mini, NodeMcu and Ledunia

### Firmware release information
Different firmware images are released based on Features and Sensors selection guided by code and memory usage.

- The Minimal version allows intermediate OTA uploads to support larger versions and does NOT change any persistent parameter.
- The Classic version allows single OTA uploads as did the previous Sonoff-Tasmota versions.

#### Available Features and Sensors

| Feature or Sensor              | sonoff | classic | minimal | knx | allsensors |
|--------------------------------|--------|---------|---------|-----|------------|
| MY_LANGUAGE en-GB              | x | x | x | x | x |
| MQTT_LIBRARY_TYPE PUBSUBCLIENT | x | x | x | x | x |
| USE_DOMOTICZ                   | x | x | - | x | x |
| USE_HOME_ASSISTANT             | x | x | - | x | x |
| USE_MQTT_TLS                   | - | - | - | - | - |
| USE_KNX                        | - | - | - | x | - |
| USE_WEBSERVER                  | x | x | x | x | x |
| USE_EMULATION                  | x | x | - | - | x |
| USE_DISCOVERY                  | x | x | - | x | x |
| WEBSERVER_ADVERTISE            | x | x | - | x | x |
| MQTT_HOST_DISCOVERY            | x | x | - | x | x |
| USE_TIMERS                     | x | - | - | x | x |
| USE_TIMERS_WEB                 | x | - | - | x | x |
| USE_SUNRISE                    | x | - | - | x | x |
| USE_RULES                      | x | - | - | x | x |
|                                |   |   |   |   |   |
| USE_ADC_VCC                    | x | x | x | x | x |
| USE_DS18B20                    | x | x | - | x | - |
| USE_DS18x20                    | - | - | - | - | x |
| USE_DS18x20_LEGACY             | - | - | - | - | - |
| USE_I2C                        | x | x | - | x | x |
| USE_SHT                        | x | x | - | x | x |
| USE_SHT3X                      | x | x | - | x | x |
| USE_HTU                        | x | x | - | x | x |
| USE_BMP                        | x | x | - | x | x |
| USE_BME680                     | - | - | - | - | x |
| USE_SGP30                      | x | - | - | x | x |
| USE_BH1750                     | x | x | - | x | x |
| USE_VEML6070                   | - | - | - | - | x |
| USE_TSL2561                    | - | - | - | - | x |
| USE_SI1145                     | - | - | - | - | x |
| USE_ADS1115                    | - | - | - | - | x |
| USE_ADS1115_I2CDEV             | - | - | - | - | - |
| USE_INA219                     | - | - | - | - | x |
| USE_MGS                        | - | - | - | - | x |
| USE_SPI                        | - | - | - | - | - |
| USE_MHZ19                      | x | x | - | x | x |
| USE_SENSEAIR                   | x | x | - | x | x |
| USE_PMS5003                    | x | x | - | x | x |
| USE_NOVA_SDS                   | x | - | - | x | x |
| USE_PZEM004T                   | x | x | - | x | x |
| USE_SERIAL_BRIDGE              | x | - | - | x | x |
| USE_SDM120                     | - | - | - | - | x |
| USE_IR_REMOTE                  | x | x | - | x | x |
| USE_IR_HVAC                    | - | - | - | - | x |
| USE_IR_RECEIVE                 | x | - | - | x | x |
| USE_WS2812                     | x | x | - | x | x |
| USE_WS2812_DMA                 | - | - | - | - | - |
| USE_ARILUX_RF                  | x | x | - | x | x |
| USE_SR04                       | x | - | - | x | x |

#### Typical file size

| ESP/Arduino library version | sonoff | classic | minimal | knx  | allsensors |
|-----------------------------|--------|---------|---------|------|------------|
| ESP/Arduino lib v2.3.0      | 529k   | 490k    | 429k    | 538k | 554k       |
| ESP/Arduino lib v2.4.0      | 534k   | 498k    | 436k    | 542k | 558k       |
| ESP/Arduino lib v2.4.1      | 536k   | 501k    | 439k    | 545k | 560k       |

### Contribute
You can contribute to Sonoff-Tasmota by
- providing Pull Requests (Features, Proof of Concepts, Language files or Fixes)
- testing new released features and report issues
- donating to acquire hardware for testing and implementing or out of gratitude

[![donate](https://img.shields.io/badge/donate-PayPal-blue.svg)](https://paypal.me/tasmota)

### Credits

#### Libraries used
Libraries used with Sonoff-Tasmota are:
- [ESP8266 core for Arduino](https://github.com/esp8266/Arduino)
- [Adafruit BME680](https://github.com/adafruit/Adafruit_BME680)
- [Adafruit Sensor](https://github.com/adafruit/Adafruit_Sensor)
- [Adafruit SGP30](https://github.com/adafruit/Adafruit_SGP30)
- [ArduinoJson](https://arduinojson.org/)
- [Esp8266MqttClient](https://github.com/tuanpmt/ESP8266MQTTClient)
- [esp-knx-ip](https://github.com/envy/esp-knx-ip)
- [esp-mqtt-arduino](https://github.com/i-n-g-o/esp-mqtt-arduino)
- [I2Cdevlib](https://github.com/jrowberg/i2cdevlib)
- [IRremoteEsp8266](https://github.com/markszabo/IRremoteESP8266)
- [JobaTsl2561](https://github.com/joba-1/Joba_Tsl2561)
- [MultiChannelGasSensor](http://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/)
- [NeoPixelBus](https://github.com/Makuna/NeoPixelBus)
- [OneWire](https://github.com/PaulStoffregen/OneWire)
- [PubSubClient](https://github.com/knolleary/pubsubclient)

#### People inspiring me
People helping to keep the show on the road:
- David Lang providing initial issue resolution and code optimizations
- Heiko Krupp for his IRSend, HTU21, SI70xx and Wemo/Hue emulation drivers
- Wiktor Schmidt for Travis CI implementation
- Thom Dietrich for PlatformIO optimizations
- Marinus van den Broek for his EspEasy groundwork
- Pete Ba for more user friendly energy monitor calibration
- Lobradov providing compile optimization tips
- Flexiti for his initial timer implementation
- reloxx13 for his [SonWeb](https://github.com/reloxx13/SonWEB) management tool
- Joachim Banzhaf for his TSL2561 library and driver
- Gijs Noorlander for his MHZ19 and SenseAir drivers
- Emontnemery for his HomeAssistant Discovery concept and many code tuning tips
- Aidan Mountford for his HSB support
- Daniel Ztolnai for his Serial Bridge implementation
- Gerhard Mutz for his SGP30 and Sunrise/Sunset driver
- Nuno Ferreira for his HC-SR04 driver
- Adrian Scillato for his (security)fixes and implementing and maintaining KNX
- Gennaro Tortone for implementing and maintaining Eastron drivers
- Raymond Mouthaan for managing Wemos Wiki information
- Norbert Richter, Frogmore42 and Jason2866 for providing many issue answers
- Many more providing Tips, Pocs or PRs

### License

This program is licensed under GPL-3.0
