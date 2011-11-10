/* 
* Some Code adapted from timer interrupt example by Sebastian Wallin
* http://popdevelop.com/2010/04/mastering-timer-interrupts-on-the-arduino/
*/  
   
/* Timer2 reload value, globally available */  
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
#define FREQ1 6
#define FREQ2 9
#define FREQ3 10
#define FREQ4 11
#define FREQ5 1
   
/* Setup phase: configure and enable timer2 overflow interrupt */  
void setup() {  
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
   * The following loads the value 131 into the Timer 2 counter register 
   * The math behind this is: 
   * (CPU frequency) / (prescaler value) = 125000 Hz = 8us. 
   * (desired period) / 8us = 1. 
   * MAX(uint8) - 10 = 255; 
   */  
  /* Save value globally for later reload in ISR */  
  tcnt2 = 255;   
  
  /* Finally load end enable the timer */  
  TCNT2 = tcnt2;  
  TIMSK2 |= (1<<TOIE2);  
}  
  
/* 
 * Install the Interrupt Service Routine (ISR) for Timer2 overflow. 
 * This is normally done by writing the address of the ISR in the 
 * interrupt vector table but conveniently done by using ISR()  */  
ISR(TIMER2_OVF_vect) {  
  /* Reload the timer */  
  TCNT2 = tcnt2;  
  
  count1++; count2++; count3++; count4++; count5++; 
  
  if (count1 == 342)
  {
    digitalWrite(FREQ1, toggle1 == 0 ? HIGH : LOW);  
    toggle1 = ~toggle1;
    count1 = 0;
  } 
  if (count2 == 310)
  {
    digitalWrite(FREQ2, toggle2 == 0 ? HIGH : LOW);  
    toggle2 = ~toggle2;
    count2 = 0;
  }
  if (count3 == 280)
  {
    digitalWrite(FREQ3, toggle3 == 0 ? HIGH : LOW);  
    toggle3 = ~toggle3;
    count3 = 0;
  }
  if (count4 == 239)
  {
    digitalWrite(FREQ4, toggle4 == 0 ? HIGH : LOW);  
    toggle4 = ~toggle4;
    count4 = 0;
  }
  if (count5 == 215)
  {
    digitalWrite(FREQ5, toggle5 == 0 ? HIGH : LOW);  
    toggle5 = ~toggle5;
    count5 = 0;
  } 
}  
  
/* Main loop. Empty, but needed to avoid linker errors */  
void loop() {  
}
