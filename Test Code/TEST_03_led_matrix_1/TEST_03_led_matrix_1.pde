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
#define MOSI  11 
#define SCLK  13
#define CS   10

void setup() 
{  
  //SPI Bus setup
  SPCR = (1<<SPE)|(1<<MSTR)|(1<<SPR1);	//Enable SPI HW, Master Mode, divide clock by 16    //SPI Bus setup
  
  //Set the pin modes for the RGB matrix
  pinMode(MOSI, OUTPUT);
  pinMode(SCLK, OUTPUT);
  pinMode(CS,  OUTPUT);
  
  digitalWrite(CS, HIGH);
  delay(10);

} 
 
void loop() 
{
for(int matrix=1; matrix <=3; matrix++)
{ 
 digitalWrite(CS, LOW);
 delay(1);
  //Send the color buffer to the RGB Matrix
    for(int LED=0; LED<64; LED++)
    {
        spi_transfer(BLACK);
    }
  //Deactivate the RGB matrix.
  delay(1);
  digitalWrite(CS, HIGH);
  delay(10);
}

 digitalWrite(CS, LOW);
 delay(1);
  //Send the color buffer to the RGB Matrix
    for(int LED=0; LED<64; LED++)
    {
      if (LED == 0)
        spi_transfer(GREEN);
      else if (LED == 1)
        spi_transfer(RED);
      else if (LED == 2)
        spi_transfer(MAGENTA);
      else
        spi_transfer(BLACK);
    }
  //Deactivate the RGB matrix.
  delay(1);
  digitalWrite(CS, HIGH);
  delay(10);


} 


//Use this command to send a single color value to the RGB matrix.
//NOTE: You must send 64 color values to the RGB matrix before it displays an image!
char spi_transfer(volatile char data)
{
  SPDR = data;                    // Start the transmission
  while (!(SPSR & (1<<SPIF)))     // Wait for the end of the transmission
  {
  };
  return SPDR;                    // return the received byte
}
