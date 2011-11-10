
//==============================
//General Definitions
//==============================
#define MYUBRR	1	//Sets 57600 Baud using 1 Mhz Clock

#define RED		0xE0
#define GREEN	0x1C
#define BLUE	0x07
#define YELLOW	0xFC
#define TEAL	0x1F
#define WHITE	0xFF
#define BLACK	0x00

//==============================
//PortB
//==============================
#define CS	2
#define MOSI	3
#define MISO	4
#define SCK		5

//==============================
//PortD
//==============================
#define RX_IN	0
#define TX_OUT	1

//==============================
//Global Macro Definitions
//==============================
#define sbi(var, mask)   ((var) |= (uint8_t)(1 << mask))
#define cbi(var, mask)   ((var) &= (uint8_t)~(1 << mask))

//==============================
//Function Definitions
//==============================
void ioinit(void);      
static int uart_putchar(char c, FILE *stream);
uint8_t uart_getchar(void);
static FILE mystdout = FDEV_SETUP_STREAM(uart_putchar, NULL, _FDEV_SETUP_WRITE);
uint8_t spi_exch(uint8_t output);
void delay_ms(uint16_t x); 
void putchar_frame(char *message, int position, char color);
uint8_t wait4_char(void);
