//Define the "Normal" Colors
#define BLACK  0
#define RED  0xE0
#define GREEN  0x1C
#define BLUE  0x03
#define ORANGE  RED|GREEN
#define MAGENTA  RED|BLUE
#define TEAL  BLUE|GREEN
#define WHITE (RED|GREEN|BLUE)-0xA0

//Define the SPI Pin Numbers
#define MOSI  3 
#define SCLK  4
#define CS1   12
#define CS2   13
#define CS3   7
#define CS4   8
#define CS_POT 2

//Include Pitch Definitions
#include "pitches.h"

//Speaker Tone (Frequency Control)
#define SP1FREQ  9      //Speaker 1 Frequency

//IR Sensor Analog Input Pins
#define IR1  0           //Infrared input 1

void setup() 
{    
  //Set the pin modes for the RGB matrix
  pinMode(MOSI, OUTPUT);
  pinMode(SCLK, OUTPUT);
  pinMode(CS1,  OUTPUT);
  pinMode(CS2,  OUTPUT);
  pinMode(CS3,  OUTPUT);
  pinMode(CS4,  OUTPUT);
  
  //Set Speaker Pin Modes
  pinMode(SP1FREQ,  OUTPUT);
  pinMode(IR1,  INPUT);
  pinMode(CS_POT, OUTPUT);
  
  digitalWrite(CS1, HIGH);
  digitalWrite(CS2, HIGH);
  digitalWrite(CS3, HIGH);
  digitalWrite(CS4, HIGH);
  digitalWrite(CS_POT, HIGH);
  delay(10);

  //Set Initial Volume at zero
  digitalWrite(CS_POT, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, 0);
  shiftOut(MOSI, SCLK, MSBFIRST, 0);
  digitalWrite(CS_POT, HIGH);


   //Play Tone
  tone(SP1FREQ, NOTE_E3);
  
  //Start Serial Debug
  Serial.begin(9600);

} 

//Send a single color value to the RGB matrix.
//NOTE: You must send 64 color values to the RGB matrix before it displays an image!
void send_color(int CS_num, char data)
{
  digitalWrite(CS_num, LOW);
  //delayMicroseconds(500);
  shiftOut(MOSI, SCLK, MSBFIRST, data);
  //delayMicroseconds(500);
  digitalWrite(CS_num, HIGH);
}
 
void loop() 
{
  
  int vol = map(analogRead(IR1), 40, 700, 0, 255);
  Serial.println(vol);
  if (vol > 255) vol = 255;
  if (vol < 0) vol = 0;
  digitalWrite(CS_POT, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, 0);
  shiftOut(MOSI, SCLK, MSBFIRST, vol);
  digitalWrite(CS_POT, HIGH);
  
    
} 
