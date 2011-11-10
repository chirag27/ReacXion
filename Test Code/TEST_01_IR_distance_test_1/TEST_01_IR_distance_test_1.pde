//Pins for Digital Potentiometer SPI Comm
const int CS_L      = 3;     //Chip Select  
const int MOSI      = 7;     //Master Out, Slave In
const int SCLK      = 8;     //SPI Clock

//Digital Potentiometer Registers (Volume Control)
const int SP1_reg  = 0;      //Speaker 1 Register

//Speaker PWM (Frequency Control)
const int SP1 = 11;          //Speaker 1 Frequency

//IR Sensor Analog Input Pins
const int IR1 = 0;           //Infrared input 1

void setup()
{
  //Set Pin Direction
  pinMode(CS_L, OUTPUT);
  pinMode(SCLK, OUTPUT);
  pinMode(MOSI, OUTPUT);
  pinMode(SP1,  OUTPUT);
  pinMode(IR1,  INPUT );
  
  //Set Chip Select to default value
  digitalWrite(CS_L, HIGH);
  
  //Initialize Speakers to Lowest Volume
  digitalWrite(CS_L, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, SP1_reg);
  shiftOut(MOSI, SCLK, MSBFIRST, 0);
  digitalWrite(CS_L, HIGH);
  
  //Setup Serial Communication for Debugging
  Serial.begin(9600);
}

void loop()
{
  //Read the Sensor Values
  int SP1_val = map(analogRead(IR1), 0, 1023, 0, 255);
  Serial.println(SP1_val);
  delay(300);
    
  //Set Speaker Volume

  digitalWrite(CS_L, LOW);
  shiftOut(MOSI, SCLK, MSBFIRST, SP1_reg);
  shiftOut(MOSI, SCLK, MSBFIRST, SP1_val);
  digitalWrite(CS_L, HIGH);

  //Play Tone
  tone(SP1, 33);
  
}
