/* 
 *
 * 
 * Arjan Vreugdenhil | Bangedaon
 */

#include <Arduino.h>
#include "ESP8266mDNS.h"
#include <WiFiManager.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>

#define API_PORT 80

#define LIGHT_BLINK_SPEED 500

#define LIGHT_PIN_RED D0
#define LIGHT_PIN_ORANGE D1
#define LIGHT_PIN_GREEN D2
#define LIGHT_PIN_BLUE D3
#define LIGHT_PIN_WHITE D4
#define LIGHTCOUNT 5

enum light_state
{
  OFF,
  ON,
  BLINKING
};

static const String light_ids[LIGHTCOUNT] =
    {"RED",
     "ORG",
     "GRN",
     "BLU",
     "WHT"};

static const int lights[LIGHTCOUNT] = {LIGHT_PIN_RED,
                                       LIGHT_PIN_ORANGE,
                                       LIGHT_PIN_GREEN,
                                       LIGHT_PIN_BLUE,
                                       LIGHT_PIN_WHITE};

static light_state light_states[LIGHTCOUNT] = {OFF};

static unsigned long previous_light_millis;
static bool blink_state;

WiFiManager wifiManager;
AsyncWebServer server(API_PORT);

void notFound(AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
}

void setup()
{
  Serial.begin(115200);
  delay(200);

  WiFi.softAPdisconnect(true);
  if (!wifiManager.autoConnect("PrinterModule"))
  {
    Serial.println("Failed to connect and hit timeout");
    delay(3000);
    ESP.restart();
    delay(5000);
  }
  else
  {
    Serial.println("Connected.");
  }

  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    pinMode(lights[i], OUTPUT);
  }
  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    //digitalWrite(lights[i], HIGH);
    analogWrite(lights[i], 50);
  }
  delay(1000);


  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
      request->send(200, "text/plain", "Hello, world");
  });

  // Send a GET request to <IP>/get?message=<message>
  server.on("/get", HTTP_GET, [] (AsyncWebServerRequest *request) {
      String message;
      if (request->hasParam(PARAM_MESSAGE)) {
          message = request->getParam(PARAM_MESSAGE)->value();
      } else {
          message = "No message sent";
      }
      request->send(200, "text/plain", "Hello, GET: " + message);
  });

  // Send a POST request to <IP>/post with a form field message set to <message>
  server.on("/post", HTTP_POST, [](AsyncWebServerRequest *request){
      String message;
      if (request->hasParam(PARAM_MESSAGE, true)) {
          message = request->getParam(PARAM_MESSAGE, true)->value();
      } else {
          message = "No message sent";
      }
      request->send(200, "text/plain", "Hello, POST: " + message);
  });

  server.onNotFound(notFound);

  server.begin();


  const int mdns_name_len = 21;
  char mdns_name[mdns_name_len];
  sprintf(mdns_name, "printermodule_%6X", ESP.getChipId());
  if (!MDNS.begin(mdns_name))
  {
      Serial.println("Error setting up MDNS responder!");
  }
  else
  {
      Serial.println("mDNS responder started");
  }
  MDNS.addService("printermdule", "tcp", API_PORT);

  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    digitalWrite(lights[i], LOW);
  }

  previous_light_millis = millis();
  blink_state = false;
}

void loop()
{
  // Set light states
  // Light State Blinking
  unsigned long current_millis = millis();
  if (current_millis > (previous_light_millis + LIGHT_BLINK_SPEED))
  {
    blink_state = !blink_state;
    
    for (int i = 0; i < LIGHTCOUNT; i++)
    {
      if (light_states[i] == BLINKING)
      {
        digitalWrite(lights[i], blink_state);
      }
    }
    previous_light_millis = current_millis;
  }
  // Light States On/Off
  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    if (light_states[i] == ON)
    {
      digitalWrite(lights[i], HIGH);
    }
    else if (light_states[i] == OFF)
    {
      digitalWrite(lights[i], LOW);
    }
  }

}
