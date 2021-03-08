#include <OneWire.h>
#include <DallasTemperature.h>


#define ONE_WIRE_BUS 2

const byte button1 = 3;
const byte buzzer = 4;

int ledState = LOW;
byte buttonState;
byte lastButtonState = HIGH;
int incByte = 0;
float lastTemp = 0.0;
int lastTempTime = 0;

unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {

    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(buzzer, OUTPUT);
    pinMode(button1, INPUT_PULLUP);
    Serial.begin(9600);
    Serial.println("Ready");
    digitalWrite(LED_BUILTIN, ledState);
    delay(500);
    lastTempTime = millis();
    sensors.begin();
}

void loop() {
    if (Serial.available() > 0) {
        incByte = Serial.parseInt();
        if (incByte == 1) {
        // Reverse state off led13 and send the current state back
            ledState = ! ledState; 
            digitalWrite(LED_BUILTIN, ledState);
            Serial.println(0);
        } else if (incByte == 2) {
        // Play a tone
            tone(buzzer, 1000, 100);
            Serial.println(0);
        } else if (incByte == 3) {
        // Send back the current state of led13
            Serial.print("13:");
            Serial.println(ledState);
        } else if (incByte == 4) {
        // Send back last temperature read
           // Serial.print("Temp:");
            Serial.println(lastTemp);
        } else {
            Serial.println(1);
        }
        
    }
        
    int reading = digitalRead(button1);
    if (reading != lastButtonState) {
        lastDebounceTime = millis();
    }

    if ((millis() - lastDebounceTime) > debounceDelay) {
        if (reading != buttonState) {
            buttonState = reading;
            if (buttonState == LOW) {
                tone(buzzer, 1000, 100);
                ledState = !ledState;
                Serial.println(ledState);
            }
        }
    }

    digitalWrite(LED_BUILTIN, ledState);
    lastButtonState = reading;
    if ((millis() - lastTempTime) > 2000) {
        sensors.requestTemperatures();
        lastTemp = sensors.getTempCByIndex(0);
        lastTempTime = millis();
    }
    /* 
    if (digitalRead(button1) == LOW) {
    digitalWrite(LED_BUILTIN, HIGH);
    tone(buzzer, 1000);
    } else {
    digitalWrite(LED_BUILTIN, LOW);
    noTone(buzzer);
    }
    if (Serial.available()) {
    unsigned long freq = Serial.read();
    tone(buzzer, freq, 2000);
    }
    */
}

