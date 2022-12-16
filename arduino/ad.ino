#include "ArduinoJson-v6.19.4.h"

struct LedControl {
  boolean ledGreen0;
  boolean ledGreen1;
  boolean ledYellow0;
  boolean ledYellow1;
  boolean ledRed0;
  boolean ledRed1;
};

LedControl ledControl = {
    .ledGreen0 = true,
    .ledGreen1 = false,
    .ledYellow0 = false,
    .ledYellow1 = false,
    .ledRed0 = false,
    .ledRed1 = false,
};

void setup() {
  Serial.begin(9600);

  // Leds: digital
  for(int i=2; i<=9; i++) {
    pinMode(i, OUTPUT);
  }
}

void loop() {
  int light = analogRead(A0);
  int temperature = analogRead(A1);
  tx(light, temperature);

  rx();
  //8.9 unused
  digitalWrite(7, boolToVoltage(ledControl.ledGreen0));
  digitalWrite(6, boolToVoltage(ledControl.ledGreen1));
  digitalWrite(5, boolToVoltage(ledControl.ledYellow0));
  digitalWrite(4, boolToVoltage(ledControl.ledYellow1));
  digitalWrite(3, boolToVoltage(ledControl.ledRed0));
  digitalWrite(2, boolToVoltage(ledControl.ledRed1));
  
  delay(500);
}

int boolToVoltage(bool b) {
    return b ? HIGH : LOW;
}

void tx(int light, int temperature) {
  // Arduino can't handle stringstream;

  DynamicJsonDocument doc(1024);
  doc["light"] = light;
  doc["temperature"] = temperature;

  serializeJson(doc, Serial);
  Serial.println("");
}

void rx() {
  if (Serial.available() > 0) {
    String json = Serial.readStringUntil('\n');

    DynamicJsonDocument doc(1024);
    deserializeJson(doc, json);

    ledControl.ledGreen0 = doc["ledGreen0"];
    ledControl.ledGreen1 = doc["ledGreen1"];
    ledControl.ledYellow0 = doc["ledYellow0"];
    ledControl.ledYellow1 = doc["ledYellow1"];
    ledControl.ledRed0 = doc["ledRed0"];
    ledControl.ledRed1 = doc["ledRed1"];
  }
}
