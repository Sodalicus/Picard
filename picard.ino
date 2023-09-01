#include <OneWire.h>
#include <DallasTemperature.h>

//Inside new DS18B20 w/o resistor sensor 0x28, 0xFF, 0x96, 0x72, 0x61, 0x17, 0x04, 0x21
//Inside DS18B20 sensor with R 0x28, 0xFF, 0xE7, 0x66, 0x61, 0x17, 0x04, 0xB7
//Outside DS18B20 sensor 0x28, 0x76, 0xAC, 0x79, 0x97, 0x00, 0x03, 0xAD

uint8_t sens_ins0[8] = { 0x28, 0xFF, 0x96, 0x72, 0x61, 0x17, 0x04, 0x21 };
//uint8_t sens_out0[8] = { 0x28, 0x76, 0xAC, 0x79, 0x97, 0x00, 0x03, 0xAD };

//### pins configuration
// Pins for night led and Pir
// led1 - mosfet's base
const int led1 = 4;
const int led2 = 5;
const int led3 = 6;
const int pir = 7;
const int ldr = A0;

// Pin for ds18b20 sesnors
#define ONE_WIRE_BUS 2

//### End of pins configuration


//### variables holding last sensors readings
float tempIns0 = 0.0;

//### variable to hold last time the sensors have been read
long lastTempTime = 0;
long timeRunning = 0; 

// variables to control/check lights
bool led1On = false;
bool led2On = false;
bool led3On = false;

unsigned long led1t0 = 0;
bool motionLightOn = false;
bool motionDetectionOn = true;
bool motionDetected = false;

// what the last time we've send status automatically
unsigned long status_t0 = 0;

const byte MAXIMUM_MESSAGE_LENGHT = 2; 

// Libs set-up
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);


void setup() {
    
    pinMode(pir, INPUT);
    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(led3, OUTPUT);


    Serial.begin(9600);

    delay(2000);

}

void loop() {

    while (Serial.available() > 0) {
         static char message[MAXIMUM_MESSAGE_LENGHT];
         static unsigned int  messageIndex = 0;
         char inByte = Serial.read();
         if (inByte !="\n" && (messageIndex < MAXIMUM_MESSAGE_LENGHT - 1) ) {
             message[messageIndex] = inByte;
             messageIndex++;    
         } else {
            //message[messageIndex] = "\0";
            //Serial.println(message);
            action(message);
            messageIndex = 0;
        }

     }


    if (motionDetectionOn == true) {
        if (digitalRead(pir) == HIGH && motionDetected == false) {
            motionDetected = true;
            //send motion detected to rasp
            if (motionLightOn == true) {
                digitalWrite(led1, HIGH);
                led1t0 = millis();
            }
        }
    }

    if (digitalRead(pir) == LOW && motionLightOn == true) {
        motionDetected = false; 
        if (((millis() - led1t0) > 60000)) {
            digitalWrite(led1, LOW);
        }
        }

    if (motionLightOn == true) {
        digitalWrite(led2, HIGH); 
    } else {
        digitalWrite(led2, LOW);
    }

    if (led1On == true) {
        digitalWrite(led1, HIGH); 
        motionLightOn = false;}
    if (led1On == false && motionLightOn == false) {
        digitalWrite(led1, LOW); }


    if (motionDetectionOn == true) {
        digitalWrite(led3, HIGH); }
    else {
        digitalWrite(led3, LOW); }

    if ((millis() - lastTempTime) > 2000) {
    // if it's been over 2 seconds since last time we've read temperature from DS18B20, then read it and save reading time.
        sensors.requestTemperatures();
        tempIns0 = sensors.getTempC(sens_ins0);
        lastTempTime = millis();
    }
/*
    if ((millis() - status_t0) > 5000) {
        status_t0 = millis();
        status();
    }
*/

    
}

void action(char  incomingArray[]) {
    if (incomingArray[0] == 'x') {
        motionLightOn = !motionLightOn;
        if (led1On == true) {
            led1On = false;}
    }
    else if (incomingArray[0] == 'y') {
        led1On = !led1On;
    }
    else if (incomingArray[0] == 'z') {
        motionDetectionOn = !motionDetectionOn;
    }
    else if (incomingArray[0] == 'l') {
        int val = 0;
        val = analogRead(ldr); 
        Serial.println(val);
    }
    else if (incomingArray[0] == 't') {
        Serial.println(tempIns0);
    }
    else {
        Serial.println(incomingArray[0]);
    }


}

void status() {
// return current state of devs/sockets and last known sensors readings
    long timeRunning = millis()/60000;
    Serial.print(";");
    Serial.print(timeRunning);
        Serial.print(":");

    if (motionDetected == true) {
        Serial.print("1");
    } else {
        Serial.print("0");
    }
        Serial.print(":");
    //print Pir output
    if (digitalRead(pir) == HIGH) {
        Serial.print("1"); 
    } else {
        Serial.print("0");
    }
        Serial.print(";");
}
