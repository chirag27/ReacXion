//**********************************//
//** ReacXion Source Code         **//
//** Jeremy Blum, Nandita Batheja **//
//** www.jeremyblum.com           **//
//**********************************//

//Include Definitions
#include "pitches.h"

//Define the "Normal" Colors
#define BLACK     0
#define RED       0xE0
#define GREEN     0x1C
#define BLUE      0x03
#define YELLOW    RED|GREEN
#define MAGENTA   RED|BLUE
#define TEAL      BLUE|GREEN
#define WHITE     (RED|GREEN|BLUE)-0xA0

//Define the SPI Pin Numbers
#define MOSI      3 
#define SCLK      4
#define CS_LED1   13
#define CS_LED2   12
#define CS_LED3   7
#define CS_LED4   8
#define CS_POT    5

//Speaker Tone (Frequency Control)
#define FREQ1     9

//Interrupt Mode Select
#define MODE      2

//IR Sensor Analog Input Pins
#define IR1       0
#define IR2       1
#define IR3       2
#define IR4       3
#define IR5       4

//Define Volume Registers
#define VOL1      0
#define VOL2      1
#define VOL3      2
#define VOL4      3
#define VOL5      4

//Variables to hold distance values
int dist1 = 0;
int dist2 = 0;
int dist3 = 0;
int dist4 = 0;
int dist5 = 0;

//Define the color_buffer variables
char color_buffer1 [64];
char color_buffer2 [64];
char color_buffer3 [64];
char color_buffer4 [64];

//Loop Counter Variable
int last = 0;

//Sets the volume for selected speaker
//NOTE: vol ranges from 0 to 255
void set_vol(int reg, int vol)
{
  digitalWrite(CS_POT, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, reg);
  shiftOut(MOSI, SCLK, MSBFIRST, vol);
  digitalWrite(CS_POT, HIGH);
}

//Gets Distance Value and scaled it correctly
//Returns value from 0-255 for use with digital potentiometer
int get_dist(int IR)
{
  int dist = map(analogRead(IR), 40, 700, 0, 255);
  if (dist > 255) dist = 255;
  if (dist < 0) dist = 0;
  return dist;
}

//Setup Function will run once at initialization
void setup() 
{    
  //Configure I/O Pin Directions
  pinMode(MOSI,     OUTPUT);
  pinMode(SCLK,     OUTPUT);
  pinMode(CS_LED1,  OUTPUT);
  pinMode(CS_LED2,  OUTPUT);
  pinMode(CS_LED3,  OUTPUT);
  pinMode(CS_LED4,  OUTPUT);
  pinMode(CS_POT,   OUTPUT);
  pinMode(FREQ1,    OUTPUT);
  pinMode(MODE,     INPUT);
  
  //Initialize Slave Select Pins to inactive State
  digitalWrite(CS_LED1, HIGH);
  digitalWrite(CS_LED2, HIGH);
  digitalWrite(CS_LED3, HIGH);
  digitalWrite(CS_LED4, HIGH);
  digitalWrite(CS_POT,  HIGH);
  delay(10);

  //Set all Initial Volumes to Zero 
  set_vol(VOL1, 0);
  set_vol(VOL2, 0);
  set_vol(VOL3, 0);
  set_vol(VOL4, 0);
  set_vol(VOL5, 0);
  
  //Initialize Displays to Black
  pattern_all_on(BLACK);
  delay(100);
  
  //Identify the Displays
  pattern_id();
  
  //Reset Displays to Black
  pattern_all_on(BLACK); 
  delay(1000);
  
  //Show Logo
  pattern_logo(RED, BLUE);
  delay(3000);
  
  //Reset Displays to Black
  pattern_all_on(BLACK);  

  //Play Tone
  tone(FREQ1, NOTE_A3);
  
  //Start Serial Debugging
  //Serial.begin(9600);

} 

void loop() 
{  
  
  //Get Distance Values
  dist1 = get_dist(IR1);
  
  //Serial.println(dist1);
  //delay(500);
  
  //Change Volume Based on Distance values  
  set_vol(VOL1, dist1);
  
  //Modulate LED Display
  if (dist1 < 30)
  {
    if (last !=1) pattern_all_on(BLACK);
    pattern_square1(GREEN);
    last = 1;
  }
  else if (dist1 < 60)
  {
    if (last !=2) pattern_all_on(BLACK);
    pattern_square2(GREEN);
    last = 2;
  }
  else if (dist1 < 90)
  {
    if (last !=3) pattern_all_on(BLACK);
    pattern_square3(GREEN);
    last = 3;
  }
  else if (dist1 < 120)
  {
    if (last !=4) pattern_all_on(BLACK);
    pattern_square4(GREEN);
    last = 4;
  }
  else if (dist1 < 150)
  {
    if (last !=5) pattern_all_on(BLACK);
    pattern_square5(GREEN);
    last = 5;
  }
  else if (dist1 < 180)
  {
    if (last !=6) pattern_all_on(BLACK);
    pattern_square6(GREEN);
    last = 6;
  }
  else if (dist1 < 210)
  {
    if (last !=7) pattern_all_on(BLACK);
    pattern_square7(GREEN);
    last = 7;
  }
  else if (dist1 < 240)
  {
    if (last !=8) pattern_all_on(BLACK);
    pattern_square8(GREEN);
    last = 8;
  }
  
} 
