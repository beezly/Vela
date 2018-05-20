## Visualight - A Sonoff LED Visualizer

A general ESP8266/Sonoff controller for WS2812/SK6812 LED Strips that has a range of FX but can also be driven externally with both Audio Visualizer and Backlighting features (simple Ambilight/Hyperion functionality).
It has a PC based GUI as well as an MQTT interface for the visualizer, and a set of controls for Home Assistant as well.
Multiple LED Strip clients can be driven by the single visualizer.  The visualizer renders for a defined set of virtual pixels which are remapped into the actual number of LED pixels per-strip.

The Sonoff-Tasmota based firmware for ESP8266 devices to control audio/video visualizations via an external Python application and Home Assistant integration.

I just made this for my own entertainment, with a lot of experimentation and learning along the way.  If it's useful to you, great!

## How it works
Generally speaking your light strip works just like you were using an LED Strip with Tasmota normally.  You have Home Assistant options for the brightness and scheme, but you also have a seperate FX Controller.
When the light is put into the External FX mode, it will stop being driven locally and start being driven by the visualizer over a UDP connection.  From here, everything is driven by the FX visualizer.
Strips can be opted in/out of control here, but their normal controls will stop working while opted in.  Music fed in via mic or audio loopback can be visualized, as can the screen border colors of the machine running the visualization.

The visualizer app can have multiple visualizations running simultaneously.  Each of these has their own name and settings.  Each of these "devices" can control as many seperate LED strips running the firmware as you'd like.  So you can always have a strict 1:1 relationship between individual strips and their visualization, or group them all together, or anywhere in between.

## Background
I wanted to add some LED strips to a few places and integrate it into my existing automation solutions.  
I'm a big fan of the Tasmota firmware for Sonoff and ESP8266 devices, so it seemed like a good starting place.  Mostly these were for lighting, but I wanted to be able to have some fun with them too.  Tastmota has pretty limited options for controlling LED Strips, but otherwise it's a solid and versatile setup with a great web interface, MQTT interface, OTA support, etc.  I wanted to keep all of this stuff for my setup if possible.

Most of the other options out there for doing LED FX were great for that, but limited in many other ways.  I decided to take a stab at integrating the two together.

I initially looked at just expanding what was there by directly adding more FX to Tasmota, but I fell down the rabbithole of wanting to do some audio visualization as well.  I stumbled across a nice existing base for this with the [Reactive Audio Strip](https://github.com/scottlawsonbc/audio-reactive-led-strip)/[Systematic-LEDs](https://github.com/not-matt/Systematic-LEDs) work.
I also figured some bias lighting/Ambilight style backlighting effects would be nice to have.  None of the existing solutions here I could find are Windows based and pretty much all of them want you to be running off a raspberry pi (which I'm not).  I decided to try out just doing my own traslation in the existing python audio visualizer core.  I haven't used python at all prior to this, so my approach is probably naive and certainly less optimal than it could otherwise be, but it works for my purposes.

Could I have just used a seperate pi here for the strips doing backlighting and ditched the ESP8266?  Sure, but it's fun to have them all be able to sync up for audio and all have the same general functionality.

## Original sources
This stuff is 90% the work of the original authors, I just crammed them all together and added some functionality and features here and there.
[Tasmota Firmware](https://github.com/arendst/Sonoff-Tasmota)
[Original Audio Reactive LEDs](https://github.com/scottlawsonbc/audio-reactive-led-strip)
[Systematic LEDs Fork](https://github.com/not-matt/Systematic-LEDs)
[Screengrabbing](https://nicholastsmith.wordpress.com/2017/08/10/poe-ai-part-4-real-time-screen-capture-and-plumbing)

## Caveats
I've seen a problem where it seems like UDP messages get queued and the strip falls behind.  Try lowering your framerate in this scenario.  Mine seemed to happen above 60 regularly.

I found that I couldn't have an active UDP stream going to the ESP8266 for FX while also maintaining the webserver or MQTT connections.  Trying to do so would cause them to fail and leak heap memory until the ESP8266 crashed.
Given that the audio/video effects are realtime, it didn't look like there'd be way to interleave them or anything either. 
So while the audio/video driven FX are live, the web and mqtt interfaces to the strip are disabled.  You have to use the FX side of the controls to drive the strip.  This includes a few non-effect messages that can be sent to the strip to change it out of audio mode, set a specific "Scheme" (local effect), change brightness, etc.

I tried UDP multicast and found that for some reason I got far worse performance.  It went from 60 fps down to ~10-15.  I tried a few solutions here, but I didn't ultimately figure out how to get multicast performance to match unicast.
As such, each strip registers itself with the visualizer and gets its own unicast stream.  If you have a whole ton of strips, you'll probably want to investigate the multicast route, although whatever code that is there isn't hooked up at the moment.

## Future steps
More reactive and non-reactive FX.  
Investigate higher performance screen grabbing techniques.

## Installation
[Please refer to Tasmota Here for the firmware](https://github.com/arendst/Sonoff-Tasmota)
[For the LED strips, please refer to these instructions regarding installation](https://github.com/scottlawsonbc/audio-reactive-led-strip)

The Home Assistant directory contains configuration entries to control the visualizer.  The mqtt entries should be fixed to reflect both the device name of your visualizer and the name of your sonoff.

The quick version is as follows :
Install the firmware onto your Sonoff or ESP8266 devices which are wired into a WS2812B or SK6812 LED Strip as normal.

Decide on a name for each seperate visualizer you want.  The default is "monitor".
You may change this in the Sonoff Console with:
fxdevice [name]

Download Anaconda 3.6 or latest
open an Anaconda prompt

conda create -n visualizer
activate visualizer
conda install numpy scipy pyqtgraph
pip install paho-mqtt
pip install pyaudio

Edit the config.py file to reflect the name of each "device" visualizer you want.  Again the default is "monitor".
Edit the mqtt address to be your broker.
cd to the directory you've installed the python to and run:
python main.py

Once the visualizer is running in the sonoff console type:
fxenable on
to start accepting input from the visualizer.

The Home Assitant controls can be used to activate or deactive each strip and change settings.


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
