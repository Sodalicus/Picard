#include <OneWire.h>
#include <DallasTemperature.h>


#define ONE_WIRE_BUS 2
// button pin, currently doesn't work
const byte button1 = 3;
// buzzer pin
const byte buzzer = 4;

// number of sockets to control
const byte numberOfDevs = 2;
// array to hold current state of the device(socket)
bool devStates[numberOfDevs] = {LOW, LOW};
// array to setup pin numbers of the devices(sockets)
byte devPin[numberOfDevs] = {13, 12};

int incByte = 0;

byte buttonState;
byte lastButtonState = HIGH;
float lastTemp = 0.0;
int lastTempTime = 0;


unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
    for (int i = 0; i < numberOfDevs; i++) {
        pinMode(devPin[i], OUTPUT);
        digitalWrite(devPin[i], devStates[i]);
    }

    pinMode(buzzer, OUTPUT);
    pinMode(button1, INPUT_PULLUP);

    Serial.begin(9600);
    Serial.println("Ready");

    delay(500);

    lastTempTime = millis();
    sensors.begin();
}

void loop() {
    if (Serial.available() > 0) {
        incByte = Serial.parseInt();
        if ((incByte <= numberOfDevs) && (incByte >= 1)) {
            devStates[incByte-1] = ! devStates[incByte-1]; 
            digitalWrite(devPin[incByte-1], devStates[incByte-1]);
            status();
        } else if (incByte == 5) {
            tone(buzzer, 1000, 100);
            status();
        } else if (incByte == 6) {
            status();
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
                devStates[0] = !devStates[0];
                digitalWrite(devPin[0], devStates[0]);
                Serial.println(devStates[0]);
            }
        }
    }

    lastButtonState = reading;
    if ((millis() - lastTempTime) > 2000) {
        sensors.requestTemperatures();
        lastTemp = sensors.getTempCByIndex(0);
        lastTempTime = millis();
    }
     
    
}
void status() {
for (int i = 0; i < numberOfDevs; i++) {
    Serial.print(devStates[i]);
    Serial.print(":");
}
Serial.print(lastTemp);
Serial.println(";");
}
