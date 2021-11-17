/* Auxiliary processor for 3d printers
 *  functionality includes vibration sensing, andon lights
 *
 * SCL to D1, SDA to d2
 * lamp red through white to D5 through D8
 * 
 * Arjan Vreugdenhil | Bangedaon
 */

#include <Arduino.h>
#include <Wire.h>
#include <LSM6.h>

#define LIGHT_PIN_RED D5
#define LIGHT_PIN_ORANGE D6
#define LIGHT_PIN_GREEN D7
#define LIGHT_PIN_WHITE D8
#define LIGHTCOUNT 4

#define LIGHT_BLINK_SPEED 700

enum light_state
{
  OFF,
  ON,
  BLINKING
};

static const int lights[LIGHTCOUNT] = {LIGHT_PIN_RED,
                                       LIGHT_PIN_ORANGE,
                                       LIGHT_PIN_GREEN,
                                       LIGHT_PIN_WHITE};
static light_state light_red_state = OFF;
static light_state light_orange_state = OFF;
static light_state light_green_state = OFF;
static light_state light_white_state = OFF;

static unsigned long previous_light_millis;
static bool blink_state;

LSM6 imu;
char report[250];
const int max_batchsize = 5000;

int batchsize;
int16_t history_x[max_batchsize];
int16_t history_y[max_batchsize];
int16_t history_z[max_batchsize];
int16_t previous_x = 0;
int16_t previous_y = 0;
int16_t previous_z = 0;

const char message_start_char = '@';
const char message_end_char = '$';
const int max_incoming_message_size = 80;
int incoming_message_size = 0;
char incoming_message[max_incoming_message_size] = {0};

void setup()
{
  batchsize = 0;

  Serial.begin(115200);
  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    pinMode(lights[i], OUTPUT);
  }
  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    digitalWrite(lights[i], HIGH);
  }
  delay(1000);

  Wire.begin();

  if (!imu.init())
  {
    Serial.println("Failed to detect and initialize IMU!");
  }
  else
  {
    imu.enableDefault();
  }

  for (int i = 0; i < LIGHTCOUNT; i++)
  {
    digitalWrite(lights[i], LOW);
  }

  previous_light_millis = millis();
  blink_state = false;
}

char *generate_acceleration_report()
{
  const int histories_count = 3;
  int16_t *histories[histories_count] = {history_x, history_y, history_z};
  int16_t max_amplitudes[3] = {0, 0, 0};
  int16_t avg_amplitudes[3] = {0, 0, 0};
  for (int i = 0; i < histories_count; i++)
  {
    int16_t max_amplitude = 0;
    int64_t total_amplitude = 0;
    for (int j = 0; j < batchsize; j++)
    {
      if (abs(histories[i][j]) > abs(max_amplitude))
      {
        max_amplitude = histories[i][j];
      }
      total_amplitude += histories[i][j];

      max_amplitudes[i] = max_amplitude;
      avg_amplitudes[i] = total_amplitude / batchsize;
    }
  }

  snprintf(report,
           sizeof(report),
           "{\"MA_X\":%d, \"MA_Y\":%d, \"MA_Z\":%d, \"AA_X\":%d, \"AA_Y\":%d, \"AA_Z\":%d, \"SC\":%d}",
           max_amplitudes[0],
           max_amplitudes[1],
           max_amplitudes[2],
           avg_amplitudes[0],
           avg_amplitudes[1],
           avg_amplitudes[2],
           batchsize);
  return report;
}

void update_acceleration_data()
{
  imu.readAcc();
  history_x[batchsize] = imu.a.x - previous_x;
  history_y[batchsize] = imu.a.y - previous_y;
  history_z[batchsize] = imu.a.z - previous_z;
  previous_x = imu.a.x;
  previous_y = imu.a.y;
  previous_z = imu.a.z;
  batchsize++;
  if (batchsize >= max_batchsize)
  {
    batchsize = 0;
  }
}

void loop()
{
  unsigned long current_millis = millis();
  if (current_millis > (previous_light_millis + LIGHT_BLINK_SPEED))
  {
    blink_state = !blink_state;

    if (light_red_state == BLINKING)
    {
      digitalWrite(LIGHT_PIN_RED, blink_state);
    }
    if (light_orange_state == BLINKING)
    {
      digitalWrite(LIGHT_PIN_ORANGE, blink_state);
    }
    if (light_green_state == BLINKING)
    {
      digitalWrite(LIGHT_PIN_GREEN, blink_state);
    }
    if (light_white_state == BLINKING)
    {
      digitalWrite(LIGHT_PIN_WHITE, blink_state);
    }

    previous_light_millis = current_millis;
  }
  update_acceleration_data();

  if (Serial.available())
  {
    char incoming_char = Serial.read();
    if (incoming_char == message_start_char)
    {
      incoming_message_size = 0;
    }
    else if (incoming_char == message_end_char)
    {
      bool return_success = true;
      bool return_silent = false;
      incoming_message[incoming_message_size] = '\0';
      if (strcmp(incoming_message, "get-acceleration") == 0)
      {
        // TODO: check for availability of data, possibly send "no data" back
        Serial.print(message_start_char);
        Serial.print("{\"result\":\"ok\", \"content\":");
        Serial.print(generate_acceleration_report());
        Serial.print("}");
        Serial.println(message_end_char);
        return_silent = true;
      }
      // RED
      else if (strcmp(incoming_message, "red-off") == 0)
      {
        digitalWrite(LIGHT_PIN_RED, LOW);
        light_red_state = OFF;
      }
      else if (strcmp(incoming_message, "red-on") == 0)
      {
        digitalWrite(LIGHT_PIN_RED, HIGH);
        light_red_state = ON;
      }
      else if (strcmp(incoming_message, "red-blink") == 0)
      {
        light_red_state = BLINKING;
      }
      // ORANGE
      else if (strcmp(incoming_message, "orange-off") == 0)
      {
        digitalWrite(LIGHT_PIN_ORANGE, LOW);
        light_orange_state = OFF;
      }
      else if (strcmp(incoming_message, "orange-on") == 0)
      {
        digitalWrite(LIGHT_PIN_ORANGE, HIGH);
        light_orange_state = ON;
      }
      else if (strcmp(incoming_message, "orange-blink") == 0)
      {
        light_orange_state = BLINKING;
      }
      // GREEN
      else if (strcmp(incoming_message, "green-off") == 0)
      {
        digitalWrite(LIGHT_PIN_GREEN, LOW);
        light_green_state = OFF;
      }
      else if (strcmp(incoming_message, "green-on") == 0)
      {
        digitalWrite(LIGHT_PIN_GREEN, HIGH);
        light_green_state = ON;
      }
      else if (strcmp(incoming_message, "green-blink") == 0)
      {
        light_green_state = BLINKING;
      }
      // WHITE
      else if (strcmp(incoming_message, "white-off") == 0)
      {
        digitalWrite(LIGHT_PIN_WHITE, LOW);
        light_white_state = OFF;
      }
      else if (strcmp(incoming_message, "white-on") == 0)
      {
        digitalWrite(LIGHT_PIN_WHITE, HIGH);
        light_white_state = ON;
      }
      else if (strcmp(incoming_message, "white-blink") == 0)
      {
        light_white_state = BLINKING;
      }
      else
      {
        return_success = false;
      }

      if (return_success && !return_silent)
      {
        Serial.print(message_start_char);
        Serial.print("{\"result\":\"ok\"}");
        Serial.println(message_end_char);
      }
      else
      {
        Serial.print(message_start_char);
        Serial.print("{\"result\":\"error\"}");
        Serial.println(message_end_char);
      }
    }
    else
    {
      if (incoming_message_size < max_incoming_message_size)
      {
        incoming_message[incoming_message_size] = incoming_char;
        incoming_message_size++;
      }
      else
      {
        incoming_message_size = 0;
      }
    }
  }
}
