http://bbs.pediy.com/showthread.php?s=&threadid=22795

sid 1.0���߿��Է�����installshield 6/7�ű��ļ� *.inx�����°��installshield�ű���ʽ�б仯��sid��֧�֡�
�°�ű���ʽ�仯���ݲο�EXETOOLS��̳��������
http://www.exetools.com/forum/showthread.php?t=6444 ����

����: //---------------------------------------------------------------------------

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

Ҳ����˵���°��.inx�ļ�ֻҪ������ĳ�����һ�£�sid 1.0�Ϳ�֧���ˡ�


1.��лikki��DIY��ʹ��sid����֧���°��installshield 6/7�ű��ļ���
2.��лijia�����Ĵ���ĸĽ���ʹ��sid�ַ����ο�������ʾ���ġ�



www.pediy.com
��ѩ������̳
2006.3.29
