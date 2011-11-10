//**********************************//
//** ReacXion LED Patterns        **//
//** Jeremy Blum, Nandita Batheja **//
//** www.jeremyblum.com           **//
//**********************************//

//Global Tracking Variables
boolean box1 = false;
boolean box2 = false;
boolean box3 = false;
boolean box4 = false;
boolean box5 = false;
boolean box6 = false;
boolean box7 = false;
boolean box8 = false;

//Send a single color value to the RGB matrix.
//data is a 64-length array of 8-bit values.
//NOTE: You must send 64 color values to the RGB matrix before it displays an image!
void send_colors(int CS_num, char data[])
{
  digitalWrite(CS_num, LOW);
  for(int LED=0; LED<64; LED++)
  {
    shiftOut(MOSI, SCLK, MSBFIRST, data[LED]);
  }
  
  digitalWrite(CS_num, HIGH);
}

//Identifies what CS pin each screen is connected to
void pattern_id()
{
  for (int i=3;  i<44; i=i+8) color_buffer1[i] = RED;
  for (int i=4;  i<45; i=i+8) color_buffer1[i] = RED;
  for (int i=48; i<64; i=i+1) color_buffer1[i] = RED;
  color_buffer1[5]  = RED;
  color_buffer1[6]  = RED;
  color_buffer1[13] = RED;
  color_buffer1[14] = RED;
  send_colors(CS_LED1, color_buffer1);
  
  delay(1000);
  
  for (int i=0;  i<16; i=i+1) color_buffer2[i] = GREEN;
  for (int i=24; i<40; i=i+1) color_buffer2[i] = GREEN;
  for (int i=48; i<64; i=i+1) color_buffer2[i] = GREEN;
  color_buffer2[16]  = GREEN;
  color_buffer2[17]  = GREEN;
  color_buffer2[46]  = GREEN;
  color_buffer2[47]  = GREEN;
  send_colors(CS_LED2, color_buffer2);
  
  delay(1000);
  
  for (int i=0;  i<16; i=i+1) color_buffer3[i] = TEAL;
  for (int i=24; i<40; i=i+1) color_buffer3[i] = TEAL;
  for (int i=48; i<64; i=i+1) color_buffer3[i] = TEAL;
  color_buffer3[16]  = TEAL;
  color_buffer3[17]  = TEAL;
  color_buffer3[40]  = TEAL;
  color_buffer3[41]  = TEAL;
  send_colors(CS_LED3, color_buffer3);
  
  delay(1000);
  
  for (int i=1;  i<64; i=i+8) color_buffer4[i] = YELLOW;
  for (int i=2;  i<64; i=i+8) color_buffer4[i] = YELLOW;
  for (int i=6;  i<32; i=i+8) color_buffer4[i] = YELLOW;
  for (int i=7;  i<32; i=i+8) color_buffer4[i] = YELLOW;
  for (int i=24; i<40; i=i+1) color_buffer4[i] = YELLOW;
  send_colors(CS_LED4, color_buffer4);
  
  delay(1000);
}

//Turns on all LEDs to a selected color
void pattern_all_on(char color)
{
  for(int LED=0; LED<64; LED++)
  {
    color_buffer1[LED] = color;
    color_buffer2[LED] = color;
    color_buffer3[LED] = color;
    color_buffer4[LED] = color;
  }
  send_colors(CS_LED1, color_buffer1);
  send_colors(CS_LED2, color_buffer2);
  send_colors(CS_LED3, color_buffer3);
  send_colors(CS_LED4, color_buffer4);
}

//Displays the ReacXion Logo
void pattern_logo(char color1, char color2)
{
  color_buffer1[7] = color2;
  color_buffer1[6] = color2;
  color_buffer1[5] = color2;
  color_buffer1[15] = color2;
  color_buffer1[14] = color2;
  color_buffer1[13] = color2;
  color_buffer1[12] = color2;
  color_buffer1[23] = color2;
  color_buffer1[22] = color2;
  color_buffer1[21] = color2;
  color_buffer1[20] = color2;
  color_buffer1[19] = color2;
  color_buffer1[30] = color2;
  color_buffer1[29] = color2;
  color_buffer1[28] = color2;
  color_buffer1[27] = color2;
  color_buffer1[26] = color2;
  color_buffer1[37] = color2;
  color_buffer1[36] = color2;
  color_buffer1[35] = color2;
  color_buffer1[34] = color2;
  color_buffer1[33] = color2;
  color_buffer1[44] = color2;
  color_buffer1[43] = color2;
  color_buffer1[42] = color2;
  color_buffer1[41] = color2;
  color_buffer1[40] = color2;
  color_buffer1[51] = color2;
  color_buffer1[50] = color2;
  color_buffer1[49] = color2;
  color_buffer1[48] = color2;
  color_buffer1[58] = color2;
  color_buffer1[57] = color2;
  color_buffer1[56] = color2;
  send_colors(CS_LED1, color_buffer1);

  color_buffer2[2] = color2;
  color_buffer2[1] = color2;
  color_buffer2[0] = color2;
  color_buffer2[11] = color2;
  color_buffer2[10] = color2;
  color_buffer2[9] = color2;
  color_buffer2[8] = color2;
  color_buffer2[20] = color2;
  color_buffer2[19] = color2;
  color_buffer2[18] = color2;
  color_buffer2[17] = color2;
  color_buffer2[16] = color2;
  color_buffer2[29] = color2;
  color_buffer2[28] = color2;
  color_buffer2[27] = color2;
  color_buffer2[26] = color2;
  color_buffer2[25] = color2;
  color_buffer2[38] = color2;
  color_buffer2[37] = color2;
  color_buffer2[36] = color2;
  color_buffer2[35] = color2;
  color_buffer2[34] = color2;
  color_buffer2[47] = color2;
  color_buffer2[46] = color2;
  color_buffer2[45] = color2;
  color_buffer2[44] = color2;
  color_buffer2[43] = color2;
  color_buffer2[55] = color2;
  color_buffer2[54] = color2;
  color_buffer2[53] = color2;
  color_buffer2[52] = color2;
  color_buffer2[63] = color2;
  color_buffer2[62] = color2;
  color_buffer2[61] = color2;
  send_colors(CS_LED2, color_buffer2);

  color_buffer3[2] = color2;
  color_buffer3[1] = color2;
  color_buffer3[0] = color2;
  color_buffer3[11] = color2;
  color_buffer3[10] = color2;
  color_buffer3[9] = color2;
  color_buffer3[8] = color2;
  color_buffer3[20] = color2;
  color_buffer3[19] = color2;
  color_buffer3[18] = color2;
  color_buffer3[17] = color2;
  color_buffer3[16] = color2;
  color_buffer3[29] = color2;
  color_buffer3[28] = color2;
  color_buffer3[27] = color2;
  color_buffer3[26] = color2;
  color_buffer3[25] = color2;
  color_buffer3[38] = color2;
  color_buffer3[37] = color2;
  color_buffer3[36] = color2;
  color_buffer3[35] = color2;
  color_buffer3[34] = color2;
  color_buffer3[47] = color2;
  color_buffer3[46] = color2;
  color_buffer3[45] = color2;
  color_buffer3[44] = color2;
  color_buffer3[43] = color2;
  color_buffer3[55] = color2;
  color_buffer3[54] = color2;
  color_buffer3[53] = color2;
  color_buffer3[52] = color2;
  color_buffer3[63] = color2;
  color_buffer3[62] = color2;
  color_buffer3[61] = color2;
  send_colors(CS_LED3, color_buffer3);

  color_buffer4[7] = color2;
  color_buffer4[6] = color2;
  color_buffer4[5] = color2;
  color_buffer4[15] = color2;
  color_buffer4[14] = color2;
  color_buffer4[13] = color2;
  color_buffer4[12] = color2;
  color_buffer4[23] = color2;
  color_buffer4[22] = color2;
  color_buffer4[21] = color2;
  color_buffer4[20] = color2;
  color_buffer4[19] = color2;
  color_buffer4[30] = color2;
  color_buffer4[29] = color2;
  color_buffer4[28] = color2;
  color_buffer4[27] = color2;
  color_buffer4[26] = color2;
  color_buffer4[37] = color2;
  color_buffer4[36] = color2;
  color_buffer4[35] = color2;
  color_buffer4[34] = color2;
  color_buffer4[33] = color2;
  color_buffer4[44] = color2;
  color_buffer4[43] = color2;
  color_buffer4[42] = color2;
  color_buffer4[41] = color2;
  color_buffer4[40] = color2;
  color_buffer4[51] = color2;
  color_buffer4[50] = color2;
  color_buffer4[49] = color2;
  color_buffer4[48] = color2;
  color_buffer4[58] = color2;
  color_buffer4[57] = color2;
  color_buffer4[56] = color2;
  send_colors(CS_LED4, color_buffer4);
  
  
  
  color_buffer1[7] = color1;
  color_buffer1[6] = color1;
  color_buffer1[5] = color1;
  color_buffer1[3] = color1;
  color_buffer1[2] = color1;
  color_buffer1[1] = color1;
  color_buffer1[15] = color1;
  color_buffer1[13] = color1;
  color_buffer1[11] = color1;
  color_buffer1[23] = color1;
  color_buffer1[22] = color1;
  color_buffer1[21] = color1;
  color_buffer1[19] = color1;
  color_buffer1[18] = color1;
  color_buffer1[31] = color1;
  color_buffer1[30] = color1;
  color_buffer1[27] = color1;
  color_buffer1[39] = color1;
  color_buffer1[37] = color1;
  color_buffer1[35] = color1;
  color_buffer1[34] = color1;
  color_buffer1[33] = color1;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[6] = color1;
  color_buffer2[2] = color1;
  color_buffer2[1] = color1;
  color_buffer2[15] = color1;
  color_buffer2[13] = color1;
  color_buffer2[11] = color1;
  color_buffer2[23] = color1;
  color_buffer2[22] = color1;
  color_buffer2[21] = color1;
  color_buffer2[19] = color1;
  color_buffer2[31] = color1;
  color_buffer2[29] = color1;
  color_buffer2[27] = color1;
  color_buffer2[39] = color1;
  color_buffer2[37] = color1;
  color_buffer2[34] = color1;
  color_buffer2[33] = color1;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[30] = color1;
  color_buffer3[29] = color1;
  color_buffer3[28] = color1;
  color_buffer3[25] = color1;
  color_buffer3[24] = color1;
  color_buffer3[37] = color1;
  color_buffer3[34] = color1;
  color_buffer3[45] = color1;
  color_buffer3[42] = color1;
  color_buffer3[53] = color1;
  color_buffer3[50] = color1;
  color_buffer3[62] = color1;
  color_buffer3[61] = color1;
  color_buffer3[60] = color1;
  color_buffer3[57] = color1;
  color_buffer3[56] = color1;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[29] = color1;
  color_buffer4[26] = color1;
  color_buffer4[39] = color1;
  color_buffer4[37] = color1;
  color_buffer4[36] = color1;
  color_buffer4[34] = color1;
  color_buffer4[47] = color1;
  color_buffer4[45] = color1;
  color_buffer4[43] = color1;
  color_buffer4[42] = color1;
  color_buffer4[55] = color1;
  color_buffer4[53] = color1;
  color_buffer4[50] = color1;
  color_buffer4[61] = color1;
  color_buffer4[58] = color1;
  send_colors(CS_LED4, color_buffer4);
}


//Makes Multiple Colors Square Patterns with info from all 5 sensors (mag ranges from 0-255
void pattern_multisquares(char colorA, int magA, char colorB, int magB, char colorC, int magC, char colorD, int magD, char colorE, int magE)
{
  
  if      (magA < 30)  pattern_square1(colorA);
  else if (magA < 60)  pattern_square2(colorA);
  else if (magA < 90)  pattern_square3(colorA);
  else if (magA < 120) pattern_square4(colorA);
  else if (magA < 150) pattern_square5(colorA);
  else if (magA < 180) pattern_square6(colorA);
  else if (magA < 210) pattern_square7(colorA);
  else if (magA < 240) pattern_square8(colorA);
  
  if      (magB < 30)  pattern_square1(colorB);
  else if (magB < 60)  pattern_square2(colorB);
  else if (magB < 90)  pattern_square3(colorB);
  else if (magB < 120) pattern_square4(colorB);
  else if (magB < 150) pattern_square5(colorB);
  else if (magB < 180) pattern_square6(colorB);
  else if (magB < 210) pattern_square7(colorB);
  else if (magB < 240) pattern_square8(colorB);
  
  if      (magC < 30)  pattern_square1(colorC);
  else if (magC < 60)  pattern_square2(colorC);
  else if (magC < 90)  pattern_square3(colorC);
  else if (magC < 120) pattern_square4(colorC);
  else if (magC < 150) pattern_square5(colorC);
  else if (magC < 180) pattern_square6(colorC);
  else if (magC < 210) pattern_square7(colorC);
  else if (magC < 240) pattern_square8(colorC);
  
  if      (magD < 30)  pattern_square1(colorD);
  else if (magD < 60)  pattern_square2(colorD);
  else if (magD < 90)  pattern_square3(colorD);
  else if (magD < 120) pattern_square4(colorD);
  else if (magD < 150) pattern_square5(colorD);
  else if (magD < 180) pattern_square6(colorD);
  else if (magD < 210) pattern_square7(colorD);
  else if (magD < 240) pattern_square8(colorD);
  
  if      (magE < 30)  pattern_square1(colorE);
  else if (magE < 60)  pattern_square2(colorE);
  else if (magE < 90)  pattern_square3(colorE);
  else if (magE < 120) pattern_square4(colorE);
  else if (magE < 150) pattern_square5(colorE);
  else if (magE < 180) pattern_square6(colorE);
  else if (magE < 210) pattern_square7(colorE);
  else if (magE < 240) pattern_square8(colorE); 
}

void pattern_square1(char color)
{ 
  color_buffer1[56] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[63] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[0] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[7] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square2(char color)
{ 
  color_buffer1[49] = color;
  color_buffer1[48] = color;
  color_buffer1[57] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[55] = color;
  color_buffer2[54] = color;
  color_buffer2[62] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[1] = color;
  color_buffer3[9] = color;
  color_buffer3[8] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[6] = color;
  color_buffer4[15] = color;
  color_buffer4[14] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square3(char color)
{
  color_buffer1[42] = color;
  color_buffer1[41] = color;
  color_buffer1[40] = color;
  color_buffer1[50] = color;
  color_buffer1[58] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[47] = color;
  color_buffer2[46] = color;
  color_buffer2[45] = color;
  color_buffer2[53] = color;
  color_buffer2[61] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[2] = color;
  color_buffer3[10] = color;
  color_buffer3[18] = color;
  color_buffer3[17] = color;
  color_buffer3[16] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[5] = color;
  color_buffer4[13] = color;
  color_buffer4[23] = color;
  color_buffer4[22] = color;
  color_buffer4[21] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square4(char color)
{ 
  color_buffer1[35] = color;
  color_buffer1[34] = color;
  color_buffer1[33] = color;
  color_buffer1[32] = color;
  color_buffer1[43] = color;
  color_buffer1[51] = color;
  color_buffer1[59] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[39] = color;
  color_buffer2[38] = color;
  color_buffer2[37] = color;
  color_buffer2[36] = color;
  color_buffer2[44] = color;
  color_buffer2[52] = color;
  color_buffer2[60] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[3] = color;
  color_buffer3[11] = color;
  color_buffer3[19] = color;
  color_buffer3[27] = color;
  color_buffer3[26] = color;
  color_buffer3[25] = color;
  color_buffer3[24] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[4] = color;
  color_buffer4[12] = color;
  color_buffer4[20] = color;
  color_buffer4[31] = color;
  color_buffer4[30] = color;
  color_buffer4[29] = color;
  color_buffer4[28] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square5(char color)
{
  color_buffer1[28] = color;
  color_buffer1[27] = color;
  color_buffer1[26] = color;
  color_buffer1[25] = color;
  color_buffer1[24] = color;
  color_buffer1[36] = color;
  color_buffer1[44] = color;
  color_buffer1[52] = color;
  color_buffer1[60] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[31] = color;
  color_buffer2[30] = color;
  color_buffer2[29] = color;
  color_buffer2[28] = color;
  color_buffer2[27] = color;
  color_buffer2[35] = color;
  color_buffer2[43] = color;
  color_buffer2[51] = color;
  color_buffer2[59] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[4] = color;
  color_buffer3[12] = color;
  color_buffer3[20] = color;
  color_buffer3[28] = color;
  color_buffer3[36] = color;
  color_buffer3[35] = color;
  color_buffer3[34] = color;
  color_buffer3[33] = color;
  color_buffer3[32] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[3] = color;
  color_buffer4[11] = color;
  color_buffer4[19] = color;
  color_buffer4[27] = color;
  color_buffer4[39] = color;
  color_buffer4[38] = color;
  color_buffer4[37] = color;
  color_buffer4[36] = color;
  color_buffer4[35] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square6(char color)
{
  color_buffer1[21] = color;
  color_buffer1[20] = color;
  color_buffer1[19] = color;
  color_buffer1[18] = color;
  color_buffer1[17] = color;
  color_buffer1[16] = color;
  color_buffer1[29] = color;
  color_buffer1[37] = color;
  color_buffer1[45] = color;
  color_buffer1[53] = color;
  color_buffer1[61] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[23] = color;
  color_buffer2[22] = color;
  color_buffer2[21] = color;
  color_buffer2[20] = color;
  color_buffer2[19] = color;
  color_buffer2[18] = color;
  color_buffer2[26] = color;
  color_buffer2[34] = color;
  color_buffer2[42] = color;
  color_buffer2[50] = color;
  color_buffer2[58] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[5] = color;
  color_buffer3[13] = color;
  color_buffer3[21] = color;
  color_buffer3[29] = color;
  color_buffer3[37] = color;
  color_buffer3[45] = color;
  color_buffer3[44] = color;
  color_buffer3[43] = color;
  color_buffer3[42] = color;
  color_buffer3[41] = color;
  color_buffer3[40] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[2] = color;
  color_buffer4[10] = color;
  color_buffer4[18] = color;
  color_buffer4[26] = color;
  color_buffer4[34] = color;
  color_buffer4[47] = color;
  color_buffer4[46] = color;
  color_buffer4[45] = color;
  color_buffer4[44] = color;
  color_buffer4[43] = color;
  color_buffer4[42] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square7(char color)
{
  color_buffer1[14] = color;
  color_buffer1[13] = color;
  color_buffer1[12] = color;
  color_buffer1[11] = color;
  color_buffer1[10] = color;
  color_buffer1[9] = color;
  color_buffer1[8] = color;
  color_buffer1[22] = color;
  color_buffer1[30] = color;
  color_buffer1[38] = color;
  color_buffer1[46] = color;
  color_buffer1[54] = color;
  color_buffer1[62] = color;
  send_colors(CS_LED1, color_buffer1);

  color_buffer2[15] = color;
  color_buffer2[14] = color;
  color_buffer2[13] = color;
  color_buffer2[12] = color;
  color_buffer2[11] = color;
  color_buffer2[10] = color;
  color_buffer2[9] = color;
  color_buffer2[17] = color;
  color_buffer2[25] = color;
  color_buffer2[33] = color;
  color_buffer2[41] = color;
  color_buffer2[49] = color;
  color_buffer2[57] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[6] = color;
  color_buffer3[14] = color;
  color_buffer3[22] = color;
  color_buffer3[30] = color;
  color_buffer3[38] = color;
  color_buffer3[46] = color;
  color_buffer3[54] = color;
  color_buffer3[53] = color;
  color_buffer3[52] = color;
  color_buffer3[51] = color;
  color_buffer3[50] = color;
  color_buffer3[49] = color;
  color_buffer3[48] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[1] = color;
  color_buffer4[9] = color;
  color_buffer4[17] = color;
  color_buffer4[25] = color;
  color_buffer4[33] = color;
  color_buffer4[41] = color;
  color_buffer4[55] = color;
  color_buffer4[54] = color;
  color_buffer4[53] = color;
  color_buffer4[52] = color;
  color_buffer4[51] = color;
  color_buffer4[50] = color;
  color_buffer4[49] = color;
  send_colors(CS_LED4, color_buffer4);
}

void pattern_square8(char color)
{
  color_buffer1[7] = color;
  color_buffer1[6] = color;
  color_buffer1[5] = color;
  color_buffer1[4] = color;
  color_buffer1[3] = color;
  color_buffer1[2] = color;
  color_buffer1[1] = color;
  color_buffer1[0] = color;
  color_buffer1[15] = color;
  color_buffer1[23] = color;
  color_buffer1[31] = color;
  color_buffer1[39] = color;
  color_buffer1[47] = color;
  color_buffer1[55] = color;
  color_buffer1[63] = color;
  send_colors(CS_LED1, color_buffer1);
  
  color_buffer2[7] = color;
  color_buffer2[6] = color;
  color_buffer2[5] = color;
  color_buffer2[4] = color;
  color_buffer2[3] = color;
  color_buffer2[2] = color;
  color_buffer2[1] = color;
  color_buffer2[0] = color;
  color_buffer2[8] = color;
  color_buffer2[16] = color;
  color_buffer2[24] = color;
  color_buffer2[32] = color;
  color_buffer2[40] = color;
  color_buffer2[48] = color;
  color_buffer2[56] = color;
  send_colors(CS_LED2, color_buffer2);
  
  color_buffer3[7] = color;
  color_buffer3[15] = color;
  color_buffer3[23] = color;
  color_buffer3[31] = color;
  color_buffer3[39] = color;
  color_buffer3[47] = color;
  color_buffer3[55] = color;
  color_buffer3[63] = color;
  color_buffer3[62] = color;
  color_buffer3[61] = color;
  color_buffer3[60] = color;
  color_buffer3[59] = color;
  color_buffer3[58] = color;
  color_buffer3[57] = color;
  color_buffer3[56] = color;
  send_colors(CS_LED3, color_buffer3);
  
  color_buffer4[0] = color;
  color_buffer4[8] = color;
  color_buffer4[16] = color;
  color_buffer4[24] = color;
  color_buffer4[32] = color;
  color_buffer4[40] = color;
  color_buffer4[48] = color;
  color_buffer4[63] = color;
  color_buffer4[62] = color;
  color_buffer4[61] = color;
  color_buffer4[60] = color;
  color_buffer4[59] = color;
  color_buffer4[58] = color;
  color_buffer4[57] = color;
  color_buffer4[56] = color;
  send_colors(CS_LED4, color_buffer4);
}
