<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Code Generation</title>
</head>

<body>
<?php
for ($i=0; $i<count($_POST['matrix1']); $i++)
{
	echo("color_buffer1[");
	echo($_POST['matrix1'][$i]);
	echo("] = color;");
	echo("<br />");
}
echo("send_colors(CS_LED1, color_buffer1);");
echo("<br /><br />");

for ($i=0; $i<count($_POST['matrix2']); $i++)
{
	echo("color_buffer2[");
	echo($_POST['matrix2'][$i]);
	echo("] = color;");
	echo("<br />");
}
echo("send_colors(CS_LED2, color_buffer2);");
echo("<br /><br />");

for ($i=0; $i<count($_POST['matrix3']); $i++)
{
	echo("color_buffer3[");
	echo($_POST['matrix3'][$i]);
	echo("] = color;");
	echo("<br />");
}
echo("send_colors(CS_LED3, color_buffer3);");
echo("<br /><br />");

for ($i=0; $i<count($_POST['matrix4']); $i++)
{
	echo("color_buffer4[");
	echo($_POST['matrix4'][$i]);
	echo("] = color;");
	echo("<br />");
}
echo("send_colors(CS_LED4, color_buffer4);");

?>
</body>
</html>