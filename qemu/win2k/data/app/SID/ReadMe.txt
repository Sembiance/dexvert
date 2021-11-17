http://bbs.pediy.com/showthread.php?s=&threadid=22795

sid 1.0这款工具可以反编译installshield 6/7脚本文件 *.inx，但新版的installshield脚本格式有变化，sid不支持。
新版脚本格式变化内容参考EXETOOLS论坛的这帖：
http://www.exetools.com/forum/showthread.php?t=6444 即：

引用: //---------------------------------------------------------------------------

#pragma hdrstop

//---------------------------------------------------------------------------

#include <stdio.h>
#include <fcntl.h>
#include <io.h>
#define XOR_VAL 0xF1

void main (void) 
{
  int i, c;
  unsigned char b;
  // Set "stdin" and "stdout" to have binary mode
  setmode (_fileno (stdin), _O_BINARY);
  setmode (_fileno (stdout), _O_BINARY);
  // Decrypt INX
  for (i = 0; (c = getchar ()) != EOF; i++) 
  {
    c ^= XOR_VAL;
    b = (unsigned char)((c >> 2) | (c << 6)) - (i % 71);
    putchar (b);
  }
}

//---------------------------------------------------------------------------

也就是说，新版的.inx文件只要用上面的程序处理一下，sid 1.0就可支持了。


1.感谢ikki的DIY，使得sid可以支持新版的installshield 6/7脚本文件。
2.感谢ijia对中文处理的改进，使得sid字符串参考可以显示中文。



www.pediy.com
看雪技术论坛
2006.3.29
