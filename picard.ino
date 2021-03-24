#include <OneWire.h>
#include <DallasTemperature.h>
#include <dht.h>
//Inside DS18B20 sensor 0x28, 0xFF, 0xE7, 0x66, 0x61, 0x17, 0x04, 0xB7
//Outside DS18B20 sensor 0x28, 0x76, 0xAC, 0x79, 0x97, 0x00, 0x03, 0xAD
uint8_t sens_ins0[8] = { 0x28, 0xFF, 0xE7, 0x66, 0x61, 0x17, 0x04, 0xB7 };
uint8_t sens_out0[8] = { 0x28, 0x76, 0xAC, 0x79, 0x97, 0x00, 0x03, 0xAD };
// Pin for ds18b20 sesnors
#define ONE_WIRE_BUS 2
// Pin for DHT11
#define DHTPin 8
// button pin, currently doesn't work
#define  button1 3
// buzzer pin
#define buzzer 4

// number of sockets to control
const byte numberOfDevs = 4;
// array to hold current state of the device(socket)
bool devStates[numberOfDevs] = {LOW, LOW, LOW, LOW};
// array to setup pin numbers of the devices(sockets)
byte devPin[numberOfDevs] = {13, 12, 11, 10};

// variable to hold incoming number from PC->USB
int incByte = 0;

// button state for bebouncing
byte buttonState;
byte lastButtonState = HIGH;
// variiables for debouncing timings
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// variables holding last sensors readings
float temp_ins0 = 0.0;
float temp_ins1 = 0.0;
float hum_ins1 = 0.0;
float temp_out0 = 0.0;

// variable to hold reading for dht11, used by dht object
int readData = 0;
// variable to hold last time the sensors have been read
int lastTempTime = 0;
long timeRunning = 0; 



OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
dht DHT;

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
    // parse incomind data for valid number and respond accordingly
        incByte = Serial.parseInt();
        if ((incByte <= numberOfDevs) && (incByte >= 1)) {
        // if its between 1-4, change the device variable and pin state, return status
            devStates[incByte-1] = ! devStates[incByte-1]; 
            digitalWrite(devPin[incByte-1], devStates[incByte-1]);
            status();
        } else if (incByte == 5) {
        // play a tune and return current status
            tone(buzzer, 1000, 100);
            status();
        } else if (incByte == 6) {
        // just return status
            status();
        } else {
        // not a valid command, return error code.
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
    // if it's been over 2 seconds since last time we've read temperature from DS18B20, then read it and save reading time.
        sensors.requestTemperatures();
        temp_ins0 = sensors.getTempC(sens_ins0);
        temp_out0 = sensors.getTempC(sens_out0);
        //lastTemp = sensors.getTempCByIndex(0);
        readData = DHT.read11(DHTPin);
        temp_ins1 = DHT.temperature;
        hum_ins1 = DHT.humidity;
        lastTempTime = millis();
    }
     
    
}
void status() {
// return current state of devs/sockets and last known sensors readings
    for (int i = 0; i < numberOfDevs; i++) {
    timeRunning = millis()/60000;
    // print to serial
    // dev01:dev02:dev03:dev04:temp_ins0:temp_ins1:hum_ins1:temp_out0
        Serial.print(devStates[i]);
        Serial.print(":");
    }
    Serial.print(temp_ins0);
        Serial.print(":");
    Serial.print(temp_ins1);
        Serial.print(":");
    Serial.print(hum_ins1);
        Serial.print(":");
    Serial.print(temp_out0);
        Serial.print(":");
    Serial.println(timeRunning);
}
