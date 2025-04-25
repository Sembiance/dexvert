/*
 * Vocpack 2.0 Library  -  (C) 1993 Nicola Ferioli
 *
 * This program shows how to compress a file using Vocpack library functions.
 * It works on 8-bit unsigned mono samples, but it can be easily modified.
 * Link this program with one of the libraries VP_?.LIB, depending on the
 * memory model used.
 * To improve performance you can add disk buffering ( setvbuf() ).
 */

#include <stdio.h>
#include "vocpack.h"


FILE *In,	/* source file to be compressed */
     *Out;	/* destination file */


/*
 * I/O functions needed by Vocpack Library
 */

void VP_Output (int c)			/* output c to destination file */
{
 putc(c, Out);
}

void VP_OutputSeek (long Offset)	/* go to position Offset */
{
 fseek(Out, Offset, SEEK_SET);
}

/* VP_Input and VP_InputRewind are not needed when packing */
int  VP_Input (void) { return 0; }
void VP_InputRewind (void) { return; }



/*
 * MAIN
 */

void main (int argc, char *argv[])
{
 int c;			/* character read from input file */
 VP_Info Info;		/* type of data to compress */


 /* check command-line parameters */
 if (argc != 3) {
    puts("\nUsage:  COMPR <source> <dest>");
    return; }

 /* open source and destination files */
 if ( (In = fopen(argv[1], "rb")) == NULL ) {
    printf("\nFile not found %s\n", argv[1]);
    return; }

 if ( (Out = fopen(argv[2], "wb")) == NULL ) {
    printf("\nCan't create %s\n", argv[2]);
    return; }

 /* Set the type of data to compress: 8-bit unsigned mono, no alignment. */
 /* The file name is the <source> field of the command line. */
 /* Info.UnpackedLen is unused */
 Info.IsSigned = 0;
 Info.IsStereo = 0;
 Info.Is16Bit = 0;
 Info.Align = 0;
 Info.Name = argv[1];

 /* init compression routine */
 VP_InitPack(&Info);

 /* compression loop: get a character and compress it */
 while ( (c = getc(In)) != EOF )
    VP_Pack(c);

 /* end of compression */
 VP_EndPack();

 /* close files */
 fclose(In);
 fclose(Out);
}