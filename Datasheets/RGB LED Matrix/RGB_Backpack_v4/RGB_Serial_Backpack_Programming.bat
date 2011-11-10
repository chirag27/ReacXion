MODE CON:cols=120 lines=80
color 0b
TITLE Button Pad Controller SPI (hit any key to repeat, close window when done)
CLS


:start
CLS

"C:\Program Files\Atmel\AVR Tools\STK500\Stk500.exe" -e -dAtMega168 -pf -vf -if"C:\Documents and Settings\Ryan\My Documents\-- Projects --\RGB Matrix Backpack\Code\v4\RGB_Backpack_v4.hex" -fDFFF -EF9 -ms -q -cUSB -I200kHz -s

pause

goto start