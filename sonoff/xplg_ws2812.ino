/*
  xplg_ws2812.ino - ws2812 led string support for Sonoff-Tasmota

  Copyright (C) 2018  Heiko Krupp and Theo Arends

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifdef USE_WS2812
/*********************************************************************************************\
 * WS2812 RGB / RGBW Leds using NeopixelBus library
\*********************************************************************************************/

#include <NeoPixelBus.h>

#include <WiFiUdp.h>

WiFiUDP AudioPortUdp;

#define BUFFER_LEN 2048
IPAddress multicast_ip(225,255,255,240);
uint32_t multicast_port = 7777;          // Multicast address and port

#ifdef USE_WS2812_DMA
#if (USE_WS2812_CTYPE == NEO_GRB)
  NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_BRG)
  NeoPixelBus<NeoBrgFeature, Neo800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_RBG)
  NeoPixelBus<NeoRbgFeature, Neo800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_RGBW)
  NeoPixelBus<NeoRgbwFeature, Neo800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_GRBW)
  NeoPixelBus<NeoGrbwFeature, Neo800KbpsMethod> *strip = NULL;
#else   // USE_WS2812_CTYPE
  NeoPixelBus<NeoRgbFeature, Neo800KbpsMethod> *strip = NULL;
#endif  // USE_WS2812_CTYPE
#else   // USE_WS2812_DMA
#if (USE_WS2812_CTYPE == NEO_GRB)
  NeoPixelBus<NeoGrbFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_BRG)
  NeoPixelBus<NeoBrgFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_RBG)
  NeoPixelBus<NeoRbgFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_RGBW)
  NeoPixelBus<NeoRgbwFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#elif (USE_WS2812_CTYPE == NEO_GRBW)
  NeoPixelBus<NeoGrbwFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#else   // USE_WS2812_CTYPE
  NeoPixelBus<NeoRgbFeature, NeoEsp8266BitBang800KbpsMethod> *strip = NULL;
#endif  // USE_WS2812_CTYPE
#endif  // USE_WS2812_DMA

struct WsColor {
  uint8_t red, green, blue;
};

struct ColorScheme {
  WsColor* colors;
  uint8_t count;
};

bool bUDPConnected;
uint16_t localPort = 7777;
char packetBuffer[BUFFER_LEN];
uint64_t nLastDisconnect = 0;

//debugging
uint16_t fpsCounter = 0;
uint32_t secondTimer = 0;
uint8_t missedPackets = 0;
uint32_t flushedPackets = 0;
uint8_t audio_disabled_watchdog = 0;

bool bEverythingDisabled = false;

uint8_t nMaxPixels = 1;
uint8_t nHeapProblems = 0;

uint8_t nDebugLevel = 0;

#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor cDefault;
#else
  RgbColor cDefault;
#endif


WsColor kIncandescent[2] = { 255,140,20, 0,0,0 };
WsColor kRgb[3] = { 255,0,0, 0,255,0, 0,0,255 };
WsColor kChristmas[2] = { 255,0,0, 0,255,0 };
WsColor kHanukkah[2] = { 0,0,255, 255,255,255 };
WsColor kwanzaa[3] = { 255,0,0, 0,0,0, 0,255,0 };
WsColor kRainbow[7] = { 255,0,0, 255,128,0, 255,255,0, 0,255,0, 0,0,255, 128,0,255, 255,0,255 };
WsColor kFire[3] = { 255,0,0, 255,102,0, 255,192,0 };
ColorScheme kSchemes[WS2812_SCHEMES] = {
  kIncandescent, 2,
  kRgb, 3,
  kChristmas, 2,
  kHanukkah, 2,
  kwanzaa, 3,
  kRainbow, 7,
  kFire, 3 };

uint8_t kWidth[5] = {
    1,     // Small
    2,     // Medium
    4,     // Large
    8,     // Largest
  255 };   // All
uint8_t kRepeat[5] = {
    8,     // Small
    6,     // Medium
    4,     // Large
    2,     // Largest
    1 };   // All

uint8_t ws_show_next = 1;

/********************************************************************************************/

void Ws2812StripShow()
{
#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor c;
#else
  RgbColor c;
#endif

  if (Settings.light_correction) {
    for (uint16_t i = 0; i < Settings.light_pixels; i++) {
      c = strip->GetPixelColor(i);
      c.R = ledTable[c.R];
      c.G = ledTable[c.G];
      c.B = ledTable[c.B];
#if (USE_WS2812_CTYPE > NEO_3LED)
      c.W = ledTable[c.W];
#endif
      strip->SetPixelColor(i, c);
    }
  }
  strip->Show();
}

int mod(int a, int b)
{
   int ret = a % b;
   if (ret < 0) ret += b;
   return ret;
}

#define cmin(a,b) ((a)<(b)?(a):(b))

void Ws2812UpdatePixelColor(int position, struct WsColor hand_color, float offset)
{
#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor color;
#else
  RgbColor color;
#endif

  uint16_t mod_position = mod(position, (int)Settings.light_pixels);

  color = strip->GetPixelColor(mod_position);
  float dimmer = 100 / (float)Settings.light_dimmer;
  color.R = cmin(color.R + ((hand_color.red / dimmer) * offset), 255);
  color.G = cmin(color.G + ((hand_color.green / dimmer) * offset), 255);
  color.B = cmin(color.B + ((hand_color.blue / dimmer) * offset), 255);
  strip->SetPixelColor(mod_position, color);
}

/********************************************************************************************/
// In theory this could prevent bug which causes tcp memory leaks in heap
struct tcp_pcb;
extern struct tcp_pcb* tcp_tw_pcbs;
extern "C" void tcp_abort (struct tcp_pcb* pcb);

void tcpCleanup (void) {
  while (tcp_tw_pcbs)
    tcp_abort(tcp_tw_pcbs);
}

void RegisterAudioStrip( bool bAvailable )
{
  Serial.print( bAvailable?"Registering LED Strip at IP : ":"Unregistering LED Strip at IP : " );
  Serial.println( WiFi.localIP().toString().c_str() );
  if ( bAvailable )
  {
    char stopic[TOPSZ];
    snprintf_P(stopic, sizeof(stopic), PSTR( "%s/%s/%s/%s/%s/%s"), PUB_PREFIX, MQTT_VISUALIZER_PREFIX, Settings.mqtt_light_fx_topic, MQTT_LIGHTS_TOPIC, Settings.mqtt_topic, MQTT_LIGHTS_IP_TOPIC );
    Serial.println( stopic );
    MqttClient.publish(stopic, WiFi.localIP().toString().c_str(), false );//bAvailable?"on":"off", true );
  }
  else
  {
    char stopic[TOPSZ];
    snprintf_P(stopic, sizeof(stopic), PSTR( "%s/%s/%s/%s/%s/%s"), PUB_PREFIX, MQTT_VISUALIZER_PREFIX, Settings.mqtt_light_fx_topic, MQTT_LIGHTS_TOPIC, Settings.mqtt_topic, MQTT_LIGHTS_STATE_TOPIC );
    Serial.println( stopic );
    MqttClient.publish(stopic, "off", false );//bAvailable?"on":"off", true );
    if ( Settings.light_fx_enabled > 0 )
    {
      Settings.light_fx_enabled = 0;
      char command[33];
      snprintf_P(command, sizeof(command), PSTR(D_CMND_FX_ENABLE " off"));
      ExecuteCommand( command );
    }
    for ( int i = 0; i < (int)Settings.light_pixels; i++ )
    {
      strip->SetPixelColor( i, cDefault );
    }
    strip->Show();
  }
}


bool EnterUDPMode()
{
  if ( !bEverythingDisabled )
  {
    cDefault = strip->GetPixelColor(1);
    Serial.println( "Registering LED Strip with Audio Server");
    RegisterAudioStrip( true );
    delay( 500 );
    if ( MqttIsConnected() )
    {
      Serial.println( "Disabling MQTT" );
      MqttDisconnect();
    }
#ifdef USE_WEBSERVER
    if ( Settings.webserver )
    {
      Serial.println( "Disabling WebServer" );
      StopWebserver();
    }
#endif
    tcpCleanup();
    delay( 500 );
    ConnectUDP();
    bEverythingDisabled = true;
  }
}

bool ExitUDPMode()
{
  AudioPortUdp.stop();
  if ( bEverythingDisabled )
  {
    tcpCleanup();
    DisconnectUDP();
    Serial.println( "Reconnecting MQTT" );
    MqttReconnect();
#ifdef USE_WEBSERVER
    if (Settings.webserver)
    {
      Serial.println( "Reconnecting WebServer" );
      StartWebserver(Settings.webserver, WiFi.localIP());
    }
#endif
    delay( 2000 );
    Serial.println( "Unregistering LED Strip with Audio Server");
    RegisterAudioStrip( false );
    bEverythingDisabled = false;
    delay( 1000 );
    for ( int i = 0; i < (int)Settings.light_pixels; i++ )
    {
      strip->SetPixelColor( i, cDefault );
    }
    strip->Show();
  }
}

bool SpecialAudioMode()
{
// Not sure exactly why, but bigbang crashes periodically using this code
// DMA seems totally stable.  Some timing thing causes the WDT to kick in otherwise
// and in the worse case permanently hangs.  So we'll require DMA mode for this.
#ifdef USE_WS2812_DMA
    // Make sure we're on wifi before we do anything.
    if ( WL_CONNECTED == WiFi.status() && Settings.light_fx_enabled == 1 )
    {
      if ( bEverythingDisabled )
      {
        Ws2812Audio();
        return true;
      }
      else
      {
        EnterUDPMode();
      }
    }
    else
    {
      ExitUDPMode();
    }
#endif
    return false;
}

boolean DisconnectUDP()
{
  if (bUDPConnected) {
    Serial.println("Disconnecting UDP");
    nLastDisconnect = millis();
    AudioPortUdp.stopAll();
    AddLog_P(LOG_LEVEL_DEBUG, PSTR(D_LOG_UPNP D_MULTICAST_DISABLED));
    bUDPConnected = false;
  }
  return bUDPConnected;
}

boolean ConnectUDP()
{
  if (!bUDPConnected )
  {
    Serial.println("Connecting UDP");
    //if (AudioPortUdp.beginMulticast(WiFi.localIP(), multicast_ip, multicast_port)) {
    if (AudioPortUdp.begin(multicast_port)) {
      AddLog_P(LOG_LEVEL_INFO, PSTR(D_LOG_UPNP D_MULTICAST_REJOINED));
      bUDPConnected = true;
    } else {
      AddLog_P(LOG_LEVEL_INFO, PSTR(D_LOG_UPNP D_MULTICAST_JOIN_FAILED));
      bUDPConnected = false;
    }
  }
  return bUDPConnected;
}

void Ws2812RotateRight( int nPixels )
{
  strip->RotateRight( nPixels );
  strip->Show();
}

void Ws2812RotateLeft( int nPixels )
{
  strip->RotateLeft( nPixels );
  strip->Show();
}

void Ws2812Scroll()
{
  #if (USE_WS2812_CTYPE > 1)
    RgbwColor c;
    c.W = 0;
  #else
    RgbColor c;
  #endif
  c = strip->GetPixelColor( 0 );
  strip->SetPixelColor(Settings.light_pixels / 2, c);
  c = strip->GetPixelColor( Settings.light_pixels - 1 );
  strip->SetPixelColor(Settings.light_pixels / 2 - 1, c);

  strip->RotateRight( 2, Settings.light_pixels / 2, Settings.light_pixels - 1 );
  strip->RotateLeft( 2, 0, Settings.light_pixels / 2 - 1 );
  strip->Show();
}

void Ws2812AudioCommand( uint8_t R, uint8_t G, uint8_t B )
{
  char command[33];
  if ( R != 0 )
  {
  	if ( R == 10 )
  	{
  		Serial.println( "Received UDP Exit - Disabling Audio Mode");
  		snprintf_P(command, sizeof(command), PSTR(D_CMND_FX_ENABLE " 0"));
      Settings.light_fx_enabled = 0;
      ExitUDPMode();
  	}
  	else if ( R == 20 )
  	{
  		Serial.println( "Received UDP Power Off");
  		snprintf_P(command, sizeof(command), PSTR(D_CMND_POWER " OFF"));
  	}
  	else if ( R == 21 )
  	{
  		Serial.println( "Received UDP Power On");
  		snprintf_P(command, sizeof(command), PSTR(D_CMND_POWER " ON"));
  	}
  	else if ( R >= 30 && R <= 42 )
  	{
  		Serial.println( "Received UDP Scheme");
      snprintf_P(command, sizeof(command), PSTR(D_CMND_FX_ENABLE " 0"));
      ExecuteCommand( command );
      snprintf_P(command, sizeof(command), PSTR(D_CMND_SCHEME " %c"), R);
  		//snprintf_P(command, sizeof(command), PSTR(D_CMND_SCHEME " %d"), R );
  	}
  }
  else if ( G != 0 )
  {
    Serial.print( "Received UDP Dimmer Value : " );
    G -= 100;
    Serial.println( G );
    snprintf_P(command, sizeof(command), PSTR(D_CMND_DIMMER " %d"), G );
  }
  else
  {
    nDebugLevel = B;
    return;
  }

  ExecuteCommand( command );
  return;
}


void Ws2812Audio()
{
  if ( !bUDPConnected )//&& nHeap > 2000 )
  {
    if ( !ConnectUDP() )
      return;
  }
  //Serial.print( "1" );
// Use the appropirate color type
#if (USE_WS2812_CTYPE > 1)
  RgbwColor c;
  RgbwColor color;
  c.W = 0;
#else
  RgbColor c;
  RgbColor color;
#endif

  float flDimmer = (float)Settings.light_dimmer / 100.0f;

  // With UDP and TCP stuff active (mqtt/webserver) heap leaked
  // constantly.  Since we only do UDP while active, this is
  // no longer a concern.
  /*
  if ( nDebugLevel > 127 )
  {
    int nHeap = system_get_free_heap_size();
    Serial.print("Free heap:");
    Serial.println(nHeap);
    if ( nHeap < 10000 )
    {
      tcpCleanup();
    }
  }
  */
  // If we have a pixel packet, do stuff!
  if ( AudioPortUdp.parsePacket() )
  {
    //Serial.print( "2" );
    int len = AudioPortUdp.read(packetBuffer, BUFFER_LEN );

    //Serial.print( "Length : " );
    //Serial.println( len );

    uint8 nPixel_count = len / 3;

    if ( nPixel_count == 1 )
    {
      Ws2812AudioCommand( (uint8_t)packetBuffer[0], (uint8_t)packetBuffer[1], (uint8_t)packetBuffer[2] );
      return;
    }

    nMaxPixels =  max( nMaxPixels, nPixel_count );
    float flPixelWidth = ( (float)Settings.light_pixels / (float)nMaxPixels);
    packetBuffer[len] = 0;
    //strip->ClearTo(0); // Reset strip
    if ( nDebugLevel > 191 )
    {
      Serial.print( "Got Packet : " );
      Serial.println( len );
    }

    uint8_t N = 0;
    for(int i = 0; i < len; i+=3)
    {
        //Serial.print( "3" );
        if ( i + 2 > len )
        {
          Serial.println( "WTF!?!  Outside bounds of LED count!!" );
          break;
        }

        // We try to establish the max pixels based on the last pixel
        // we get sent, but for sanity checking, we max it with the pixels
        // we're trying to set...
        nMaxPixels = max( nMaxPixels, N );

        // Fade out based on dimmer value
        c.R = (uint8_t)(packetBuffer[i] * flDimmer);
        c.G = (uint8_t)(packetBuffer[i+1] * flDimmer);
        c.B = (uint8_t)(packetBuffer[i+2] * flDimmer);

        // Interpolate across our real pixel count
        int nStartPixel = ceil( N * flPixelWidth );
        int nCurrentPixel = nStartPixel;
        int nLastPixel = max( -1, (int)ceil( (N - 1) * flPixelWidth ) );
#ifdef SPEED
        strip->ClearTo( c, nStartPixel, nLastPixel );
#else
        // pct to lerp per pixel
        float flPct = 1.0f / (float)max( 1, nStartPixel - nLastPixel );
        float flT = 0.0f;
        for ( int nCurrentPixel = nStartPixel; nCurrentPixel > nLastPixel; nCurrentPixel-- )
        {
          //Serial.print( nCurrentPixel );
          color = color.LinearBlend( c, strip->GetPixelColor(max( 0, min( (int)Settings.light_pixels, nLastPixel ) ) ), flT );
          strip->SetPixelColor( nCurrentPixel, color );
          if ( nDebugLevel > 250 )
          {
            Serial.print( "Loop : " );
            Serial.print( i );
            Serial.print( " Pixel : " );
            Serial.print( nCurrentPixel );
            Serial.print( " Start Pixel : " );
            Serial.print( nStartPixel );
            Serial.print( " Last Pixel : " );
            Serial.print( nLastPixel );
            Serial.print( " Max Pixel : " );
            Serial.print( nMaxPixels );
            Serial.print( " flt : " );
            Serial.print( flT );
            Serial.print( " flPct : " );
            Serial.print( flPct );
            Serial.print( " Color : " );
            Serial.print( color.R );
            Serial.print( color.G );
            Serial.println( color.B );
          }
          flT += flPct;
        }
#endif
		    N++;
        delay(0);
    }
    fpsCounter++;
    //Serial.print( "Start " );
    strip->Show();
    //Serial.print( "End " );
  }
  delay(0);

  if (millis() - secondTimer >= 1000U)
  {
      //Serial.print( "7" );
      // feed the watchdog
      OsWatchLoop();
      //Serial.print( "8" );
      secondTimer = millis();

      if ( nDebugLevel > 15 )
      {
        Serial.print("FPS: " );
        Serial.println( fpsCounter );
      }
      if ( fpsCounter == 0 )
      {
        audio_disabled_watchdog++;
      }
      else
      {
        audio_disabled_watchdog = 0;
      }
      // If we haven't gotten anything for AUDIO_TIMEOUT seconds, just abort.
      if ( audio_disabled_watchdog > AUDIO_TIMEOUT )
      {
        ExitUDPMode();
        audio_disabled_watchdog = 0;
      }
      fpsCounter = 0;

  }
}

void Ws2812UpdateHand(int position, uint8_t index)
{
  position = (position + Settings.light_rotation) % Settings.light_pixels;

  if (Settings.flag.ws_clock_reverse) position = Settings.light_pixels -position;
  WsColor hand_color = { Settings.ws_color[index][WS_RED], Settings.ws_color[index][WS_GREEN], Settings.ws_color[index][WS_BLUE] };

  Ws2812UpdatePixelColor(position, hand_color, 1);

  uint8_t range = 1;
  if (index < WS_MARKER) range = ((Settings.ws_width[index] -1) / 2) +1;
  for (uint8_t h = 1; h < range; h++) {
    float offset = (float)(range - h) / (float)range;
    Ws2812UpdatePixelColor(position -h, hand_color, offset);
    Ws2812UpdatePixelColor(position +h, hand_color, offset);
  }
}

void Ws2812Clock()
{
  strip->ClearTo(0); // Reset strip
  int clksize = 60000 / (int)Settings.light_pixels;

  Ws2812UpdateHand((RtcTime.second * 1000) / clksize, WS_SECOND);
  Ws2812UpdateHand((RtcTime.minute * 1000) / clksize, WS_MINUTE);
  Ws2812UpdateHand(((RtcTime.hour % 12) * (5000 / clksize)) + ((RtcTime.minute * 1000) / (12 * clksize)), WS_HOUR);
  if (Settings.ws_color[WS_MARKER][WS_RED] + Settings.ws_color[WS_MARKER][WS_GREEN] + Settings.ws_color[WS_MARKER][WS_BLUE]) {
    for (byte i = 0; i < 12; i++) {
      Ws2812UpdateHand((i * 5000) / clksize, WS_MARKER);
    }
  }

  Ws2812StripShow();
}

void Ws2812GradientColor(uint8_t schemenr, struct WsColor* mColor, uint16_t range, uint16_t gradRange, uint16_t i)
{
/*
 * Compute the color of a pixel at position i using a gradient of the color scheme.
 * This function is used internally by the gradient function.
 */
  ColorScheme scheme = kSchemes[schemenr];
  uint16_t curRange = i / range;
  uint16_t rangeIndex = i % range;
  uint16_t colorIndex = rangeIndex / gradRange;
  uint16_t start = colorIndex;
  uint16_t end = colorIndex +1;
  if (curRange % 2 != 0) {
    start = (scheme.count -1) - start;
    end = (scheme.count -1) - end;
  }
  float dimmer = 100 / (float)Settings.light_dimmer;
  float fmyRed = (float)map(rangeIndex % gradRange, 0, gradRange, scheme.colors[start].red, scheme.colors[end].red) / dimmer;
  float fmyGrn = (float)map(rangeIndex % gradRange, 0, gradRange, scheme.colors[start].green, scheme.colors[end].green) / dimmer;
  float fmyBlu = (float)map(rangeIndex % gradRange, 0, gradRange, scheme.colors[start].blue, scheme.colors[end].blue) / dimmer;
  mColor->red = (uint8_t)fmyRed;
  mColor->green = (uint8_t)fmyGrn;
  mColor->blue = (uint8_t)fmyBlu;
}

void Ws2812Gradient(uint8_t schemenr)
{
/*
 * This routine courtesy Tony DiCola (Adafruit)
 * Display a gradient of colors for the current color scheme.
 *  Repeat is the number of repetitions of the gradient (pick a multiple of 2 for smooth looping of the gradient).
 */
#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor c;
  c.W = 0;
#else
  RgbColor c;
#endif

  ColorScheme scheme = kSchemes[schemenr];
  if (scheme.count < 2) return;

  uint8_t repeat = kRepeat[Settings.light_width];  // number of scheme.count per ledcount
  uint16_t range = (uint16_t)ceil((float)Settings.light_pixels / (float)repeat);
  uint16_t gradRange = (uint16_t)ceil((float)range / (float)(scheme.count - 1));
  uint16_t speed = ((Settings.light_speed * 2) -1) * (STATES / 10);
  uint16_t offset = speed > 0 ? strip_timer_counter / speed : 0;

  WsColor oldColor, currentColor;
  Ws2812GradientColor(schemenr, &oldColor, range, gradRange, offset);
  currentColor = oldColor;
  for (uint16_t i = 0; i < Settings.light_pixels; i++) {
    if (kRepeat[Settings.light_width] > 1) {
      Ws2812GradientColor(schemenr, &currentColor, range, gradRange, i +offset);
    }
    if (Settings.light_speed > 0) {
      // Blend old and current color based on time for smooth movement.
      c.R = map(strip_timer_counter % speed, 0, speed, oldColor.red, currentColor.red);
      c.G = map(strip_timer_counter % speed, 0, speed, oldColor.green, currentColor.green);
      c.B = map(strip_timer_counter % speed, 0, speed, oldColor.blue, currentColor.blue);
    }
    else {
      // No animation, just use the current color.
      c.R = currentColor.red;
      c.G = currentColor.green;
      c.B = currentColor.blue;
    }
    strip->SetPixelColor(i, c);
    oldColor = currentColor;
  }
  Ws2812StripShow();
}

void Ws2812Bars(uint8_t schemenr)
{
/*
 * This routine courtesy Tony DiCola (Adafruit)
 * Display solid bars of color for the current color scheme.
 * Width is the width of each bar in pixels/lights.
 */
#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor c;
  c.W = 0;
#else
  RgbColor c;
#endif
  uint16_t i;

  ColorScheme scheme = kSchemes[schemenr];

  uint16_t maxSize = Settings.light_pixels / scheme.count;
  if (kWidth[Settings.light_width] > maxSize) maxSize = 0;

  uint16_t speed = ((Settings.light_speed * 2) -1) * (STATES / 10);
  uint8_t offset = speed > 0 ? strip_timer_counter / speed : 0;

  WsColor mcolor[scheme.count];
  memcpy(mcolor, scheme.colors, sizeof(mcolor));
  float dimmer = 100 / (float)Settings.light_dimmer;
  for (i = 0; i < scheme.count; i++) {
    float fmyRed = (float)mcolor[i].red / dimmer;
    float fmyGrn = (float)mcolor[i].green / dimmer;
    float fmyBlu = (float)mcolor[i].blue / dimmer;
    mcolor[i].red = (uint8_t)fmyRed;
    mcolor[i].green = (uint8_t)fmyGrn;
    mcolor[i].blue = (uint8_t)fmyBlu;
  }
  uint8_t colorIndex = offset % scheme.count;
  for (i = 0; i < Settings.light_pixels; i++) {
    if (maxSize) colorIndex = ((i + offset) % (scheme.count * kWidth[Settings.light_width])) / kWidth[Settings.light_width];
    c.R = mcolor[colorIndex].red;
    c.G = mcolor[colorIndex].green;
    c.B = mcolor[colorIndex].blue;
    strip->SetPixelColor(i, c);
  }
  Ws2812StripShow();
}

/*********************************************************************************************\
 * Public
\*********************************************************************************************/

void Ws2812Init()
{
#ifdef USE_WS2812_DMA
#if (USE_WS2812_CTYPE == NEO_GRB)
  strip = new NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#elif (USE_WS2812_CTYPE == NEO_BRG)
  strip = new NeoPixelBus<NeoBrgFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#elif (USE_WS2812_CTYPE == NEO_RBG)
  strip = new NeoPixelBus<NeoRbgFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#elif (USE_WS2812_CTYPE == NEO_RGBW)
  strip = new NeoPixelBus<NeoRgbwFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#elif (USE_WS2812_CTYPE == NEO_GRBW)
  strip = new NeoPixelBus<NeoGrbwFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#else  // USE_WS2812_CTYPE
  strip = new NeoPixelBus<NeoRgbFeature, Neo800KbpsMethod>(WS2812_MAX_LEDS);  // For Esp8266, the Pin is omitted and it uses GPIO3 due to DMA hardware use.
#endif  // USE_WS2812_CTYPE
#else  // USE_WS2812_DMA
#if (USE_WS2812_CTYPE == NEO_GRB)
  strip = new NeoPixelBus<NeoGrbFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#elif (USE_WS2812_CTYPE == NEO_BRG)
  strip = new NeoPixelBus<NeoBrgFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#elif (USE_WS2812_CTYPE == NEO_RBG)
  strip = new NeoPixelBus<NeoRbgFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#elif (USE_WS2812_CTYPE == NEO_RGBW)
  strip = new NeoPixelBus<NeoRgbwFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#elif (USE_WS2812_CTYPE == NEO_GRBW)
  strip = new NeoPixelBus<NeoGrbwFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#else  // USE_WS2812_CTYPE
  strip = new NeoPixelBus<NeoRgbFeature, NeoEsp8266BitBang800KbpsMethod>(WS2812_MAX_LEDS, pin[GPIO_WS2812]);
#endif  // USE_WS2812_CTYPE
#endif  // USE_WS2812_DMA
  strip->Begin();
  Ws2812Clear();
}

void Ws2812Clear()
{
  nMaxPixels = 1;
  if ( bUDPConnected )
  {
    Serial.println("Disconnecting UDP");
    DisconnectUDP();
  }
  strip->ClearTo(0);
  strip->Show();
  ws_show_next = 1;
}

void Ws2812SetColor(uint16_t led, uint8_t red, uint8_t green, uint8_t blue, uint8_t white)
{
#if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor lcolor;
  lcolor.W = white;
#else
  RgbColor lcolor;
#endif

  lcolor.R = red;
  lcolor.G = green;
  lcolor.B = blue;
  if (led) {
    strip->SetPixelColor(led -1, lcolor);  // Led 1 is strip Led 0 -> substract offset 1
  } else {
//    strip->ClearTo(lcolor);  // Set WS2812_MAX_LEDS pixels
    for (uint16_t i = 0; i < Settings.light_pixels; i++) {
      strip->SetPixelColor(i, lcolor);
    }
  }
  strip->Show();
  ws_show_next = 1;
}

char* Ws2812GetColor(uint16_t led, char* scolor)
{
  uint8_t sl_ledcolor[4];

 #if (USE_WS2812_CTYPE > NEO_3LED)
  RgbwColor lcolor = strip->GetPixelColor(led -1);
  sl_ledcolor[3] = lcolor.W;
 #else
  RgbColor lcolor = strip->GetPixelColor(led -1);
 #endif
  sl_ledcolor[0] = lcolor.R;
  sl_ledcolor[1] = lcolor.G;
  sl_ledcolor[2] = lcolor.B;
  scolor[0] = '\0';
  for (byte i = 0; i < light_subtype; i++) {
    if (Settings.flag.decimal_text) {
      snprintf_P(scolor, 25, PSTR("%s%s%d"), scolor, (i > 0) ? "," : "", sl_ledcolor[i]);
    } else {
      snprintf_P(scolor, 25, PSTR("%s%02X"), scolor, sl_ledcolor[i]);
    }
  }
  return scolor;
}

void Ws2812ShowScheme(uint8_t scheme)
{
  switch (scheme) {
    case 0:  // Clock
      if (((STATES/10)*2 == state) || (ws_show_next)) {
        Ws2812Clock();
        ws_show_next = 0;
      }
      break;
    default:
      if (1 == Settings.light_fade) {
        Ws2812Gradient(scheme -1);
      } else {
        Ws2812Bars(scheme -1);
      }
      ws_show_next = 1;
      break;
  }
}

#endif  // USE_WS2812
