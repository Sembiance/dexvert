/*
 * Vocpack 2.0 Library  -  (C) 1993 Nicola Ferioli
 *
 * This program shows how to decompress a file using Vocpack library functions.
 * Link this program with one of the libraries VP_?.LIB, depending on the
 * memory model used.
 * To improve performance you can add disk buffering ( setvbuf() ).
 */

#include <stdio.h>
#include "vocpack.h"


FILE *In,	/* source file to be decompressed */
     *Out;	/* destination file */


/*
 * I/O functions needed by Vocpack Library
 */

int VP_Input (void)			/* input char from source file */
{
 return getc(In);
}

void VP_InputRewind (void)		/* rewind source file */
{
 rewind(In);
}

/* VP_Output and VP_OutputSeek are not needed when unpacking */
void VP_Output () { return; }
void VP_OutputSeek () { return; }



/*
 * MAIN
 */

void main (int argc, char *argv[])
{
 int c;			/* character to write to output file */


 /* check command-line parameters */
 if (argc != 3) {
    puts("\nUsage:  DECOMPR <source> <dest>");
    return; }

 /* open source and destination files */
 if ( (In = fopen(argv[1], "rb")) == NULL ) {
    printf("\nFile not found %s\n", argv[1]);
    return; }

 if ( (Out = fopen(argv[2], "wb")) == NULL ) {
    printf("\nCan't create %s\n", argv[2]);
    return; }

 /* detect source file content */
 switch (VP_InitUnpack(NULL)) {		/* NULL = discard info */
	case VP_OK:
		break;			/* ok, file can be unpacked */

	case VP_ERR_NOTVP:
		printf("\n%s is not compressed with Vocpack\n", argv[1]);
		return;

	case VP_ERR_OLDMETHOD:
		printf("\n%s is compressed with Vocpack 1.0\n", argv[1]);
		return;

	case VP_ERR_UNKMETHOD:
		printf("\n%s is compressed with an unknown method\n", argv[1]);
		return;
 }

 /* decompression loop: decompress a character and write it */
 while ( (c = VP_Unpack()) != VP_EOF )
    putc(c, Out);

 /* end of decompression */
 VP_EndUnpack();

 /* close files */
 fclose(In);
 fclose(Out);
}