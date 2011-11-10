#include "pitches.h"

//Speaker Tone (Frequency Control)
const int SP1_freq = 9;      //Speaker 1 Frequency

//IR Sensor Analog Input Pins
const int IR1 = 0;           //Infrared input 1

void setup()
{
  //Set Pin Direction
  pinMode(SP1_freq,  OUTPUT);
  pinMode(IR1,  INPUT );
   
  //Setup Serial Communication for Debugging

  
  tone(SP1_freq, NOTE_C5, 1000);
  delay(1000);
  tone(SP1_freq, NOTE_D5, 1000);
  delay(1000);
  tone(SP1_freq, NOTE_E6, 1000);
  delay(1000);
  tone(SP1_freq, NOTE_G6, 1000);
  delay(1000);
  tone(SP1_freq, NOTE_A6, 1000);
  delay(1000);
}

void loop()
{
  //Read the Sensor Values
  //int IR1_val = map(analogRead(IR1), 0, 1023, 0, 255);
    //Play Tone
  //tone(SP1_freq, NOTE_C3);
  
}
