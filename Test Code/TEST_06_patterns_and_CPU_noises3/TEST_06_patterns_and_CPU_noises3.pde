//**********************************//
//** ReacXion Source Code         **//
//** Jeremy Blum, Nandita Batheja **//
//** www.jeremyblum.com           **//
//**********************************//

/* 
* Some Code adapted from timer interrupt example by Sebastian Wallin
* http://popdevelop.com/2010/04/mastering-timer-interrupts-on-the-arduino/
*/  

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
#define CS_POT    0
#define CS_LED1   5
#define CS_LED2   6
#define CS_LED3   7
#define CS_LED4   8

//Interrupt Mode Select
#define MODE      2

//IR Sensor Analog Input Pins
#define IR1       0
#define IR2       1
#define IR3       2
#define IR4       3
#define IR5       4

//Define Volume Registers
#define VOL1 0
#define VOL2 1
#define VOL3 2
#define VOL4 3
#define VOL5 4

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


/* Timer reload value, globally available */  
unsigned int tcnt2;  
   
/* Toggle HIGH or LOW digital write */  
int toggle1 = 0; 
int toggle2 = 0; 
int toggle3 = 0; 
int toggle4 = 0; 
int toggle5 = 0; 
 
/* Counters keep track of when each note needs to be switched */
int count1 = 0;
int count2 = 0;
int count3 = 0;
int count4 = 0;
int count5 = 0;

/* Frequency Output Pins */
#define FREQ1 9
#define FREQ2 10
#define FREQ3 11
#define FREQ4 12
#define FREQ5 13


//Loop Counter Variables
int last1 = 0;
int last2 = 0;
int last3 = 0;
int last4 = 0;
int last5 = 0;
int current1 = 0;
int current2 = 0;
int current3 = 0;
int current4 = 0;
int current5 = 0;

//Arrow no-blink variable
int previous = 0;

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
  int dist = map(analogRead(IR), 50, 700, 0, 255);
  if (dist > 255) dist = 255;
  if (dist < 0) dist = 0;
  return dist;
}

//Configure Displays
void display_config(int LED_CS)
{
  digitalWrite(LED_CS, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, '%');
  shiftOut(MOSI, SCLK, MSBFIRST, 1);
  digitalWrite(LED_CS, HIGH);
}

//Update Sense Values and change volume
void sense_update()
{
  //Get Distance Values
  dist1 = get_dist(IR1);
  dist2 = get_dist(IR2);
  dist3 = get_dist(IR3);
  dist4 = get_dist(IR4);
  dist5 = get_dist(IR5);
  
  //Change Volume Based on Distance values  
  set_vol(VOL1, dist1);
  set_vol(VOL2, dist2);
  set_vol(VOL3, dist3);
  set_vol(VOL4, dist4);
  set_vol(VOL5, dist5);
}

//Setup Function will run once at initialization
void setup() 
{ 

  /* First disable the timer overflow interrupt while we're configuring */  
  TIMSK2 &= ~(1<<TOIE2);  
  
  /* Configure timer2 in normal mode (pure counting, no PWM etc.) */  
  TCCR2A &= ~((1<<WGM21) | (1<<WGM20));  
  TCCR2B &= ~(1<<WGM22);  
  
  /* Select clock source: internal I/O clock */  
  ASSR &= ~(1<<AS2);  
  
  /* Disable Compare Match A interrupt enable (only want overflow) */  
  TIMSK2 &= ~(1<<OCIE2A);  
  
  /* Now configure the prescaler to CPU clock divided by 128 */  
  TCCR2B |= (1<<CS22)  | (1<<CS20); // Set bits  
  TCCR2B &= ~(1<<CS21);             // Clear bit  
  
  /* We need to calculate a proper value to load the timer counter. 
   * The following loads the value 248 into the Timer 2 counter register 
   * The math behind this is: 
   * (Desired period) = 64us.
   * (CPU frequency) / (prescaler value) = 125000 Hz -> 8us. 
   * (desired period) / 8us = 8. 
   * MAX(uint8) - 8 = 248; 
   */  
  /* Save value globally for later reload in ISR */  
  tcnt2 = 248;   
  
  /* Finally load end enable the timer */  
  TCNT2 = tcnt2;  
  TIMSK2 |= (1<<TOIE2);

  
  //Configure I/O Pin Directions
  pinMode(MOSI,     OUTPUT);
  pinMode(SCLK,     OUTPUT);
  pinMode(CS_LED1,  OUTPUT);
  pinMode(CS_LED2,  OUTPUT);
  pinMode(CS_LED3,  OUTPUT);
  pinMode(CS_LED4,  OUTPUT);
  pinMode(CS_POT,   OUTPUT);
  pinMode(FREQ1,    OUTPUT);
  pinMode(FREQ2,    OUTPUT);
  pinMode(FREQ3,    OUTPUT);
  pinMode(FREQ4,    OUTPUT);
  pinMode(FREQ5,    OUTPUT);
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
  
  //Configure Each Display for Single Mode
  display_config(CS_LED1);
  display_config(CS_LED2);
  display_config(CS_LED3);
  display_config(CS_LED4);
  
  
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

  //Serial.begin(9600);

} 


/* 
 * Install the Interrupt Service Routine (ISR) for Timer2 overflow. 
 * This is normally done by writing the address of the ISR in the 
 * interrupt vector table but conveniently done by using ISR()  */  
ISR(TIMER2_OVF_vect) {  
  /* Reload the timer */  
  TCNT2 = tcnt2;  
  
  count1++; count2++; count3++; count4++; count5++;
  
  if (count1 == 60)
  {
    digitalWrite(FREQ1, toggle1 == 0 ? HIGH : LOW);  
    toggle1 = ~toggle1;
    count1 = 0;
  } 
  if (count2 == 53)
  {
    digitalWrite(FREQ2, toggle2 == 0 ? HIGH : LOW);  
    toggle2 = ~toggle2;
    count2 = 0;
  }
  if (count3 == 47)
  {
    digitalWrite(FREQ3, toggle3 == 0 ? HIGH : LOW);  
    toggle3 = ~toggle3;
    count3 = 0;
  }
  if (count4 == 40)
  {
    digitalWrite(FREQ4, toggle4 == 0 ? HIGH : LOW);  
    toggle4 = ~toggle4;
    count4 = 0;
  }
  if (count5 == 35)
  {
    digitalWrite(FREQ5, toggle5 == 0 ? HIGH : LOW);  
    toggle5 = ~toggle5;
    count5 = 0;
  }   
}


void loop() 
{  
   
  
  //Modulate LED Display
  //pattern_all_on(BLACK);
  //pattern_multisquares(GREEN, RED, YELLOW, MAGENTA, TEAL, WHITE);
  
  
  previous = follow_hand (GREEN, 100, previous);
  
  /*
  if (dist1 < 30)
  {
    if (last1 !=1) pattern_all_on(BLACK);
    pattern_square1(GREEN);
    last1 = 1;
  }
  else if (dist1 < 60)
  {
    if (last1 !=2) pattern_all_on(BLACK);
    pattern_square2(GREEN);
    last1 = 2;
  }
  else if (dist1 < 90)
  {
    if (last1 !=3) pattern_all_on(BLACK);
    pattern_square3(GREEN);
    last1 = 3;
  }
  else if (dist1 < 120)
  {
    if (last1 !=4) pattern_all_on(BLACK);
    pattern_square4(GREEN);
    last1 = 4;
  }
  else if (dist1 < 150)
  {
    if (last1 !=5) pattern_all_on(BLACK);
    pattern_square5(GREEN);
    last1 = 5;
  }
  else if (dist1 < 180)
  {
    if (last1 !=6) pattern_all_on(BLACK);
    pattern_square6(GREEN);
    last1 = 6;
  }
  else if (dist1 < 210)
  {
    if (last1 !=7) pattern_all_on(BLACK);
    pattern_square7(GREEN);
    last1 = 7;
  }
  else if (dist1 < 240)
  {
    if (last1 !=8) pattern_all_on(BLACK);
    pattern_square8(GREEN);
    last1 = 8;
  }
  */
  
} 
