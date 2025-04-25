/*
 * Vocpack 2.0 Library  -  (C) 1993 Nicola Ferioli
 *
 * Include file VOCPACK.H
 */

#ifndef __VOCPACK_H
#define __VOCPACK_H


#define VP_OK                   0       /* no error */
#define VP_ERR_NOTVP            1       /* file not compressed with Vocpack */
#define VP_ERR_OLDMETHOD        2       /* compressed with version 1.0 */
#define VP_ERR_UNKMETHOD        3       /* compressed with version > 2.0 */

#define VP_EOF                 -1       /* EOF returned by VP_Unpack() */

typedef struct {
	unsigned int IsSigned : 1;      /* 0 = unsigned data, 1 = signed */
	unsigned int IsStereo : 1;      /* 0 = mono, 1 = stereo */
	unsigned int Is16Bit  : 1;      /* 0 = 8 bits, 1 = 16 bits */
	unsigned int Align    : 2;      /* 16-bit samples alignment (0..3) */
	unsigned int          : 4;      /* don't care */

	char *Name;                     /* file name */
	long UnpackedLen;               /* unpacked length */

 } VP_Info;


void VP_InitPack (VP_Info *Info);
void VP_Pack (int c);
void VP_EndPack (void);

int  VP_InitUnpack (VP_Info *Info);
int  VP_Unpack (void);
void VP_EndUnpack (void);

int VP_GetInfo (VP_Info *Info);


/*
 * User supplied I/O functions
 */

int  VP_Input (void);                   /* { return getc(In); } */
void VP_Output (int c);                 /* { putc(c, Out); } */
void VP_InputRewind (void);             /* { rewind(In); } */
void VP_OutputSeek (long Offset);       /* { fseek(Out, Offset, SEEK_SET); } */


#endif
