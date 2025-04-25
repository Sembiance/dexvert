/*
 * Vocpack 2.0 Library  -  (C) 1993 Nicola Ferioli
 *
 * This program shows information about a file compressed with Vocpack.
 * Link this program with one of the libraries VP_?.LIB, depending on the
 * memory model used.
 */

#include <stdio.h>
#include "vocpack.h"


FILE *In;	/* source file */

char 	*WriteSize[2] = {"8-bit","16-bit"},	/* samples description */
	*WriteSign[2] = {"unsigned","signed"},
	*WriteStereo[2] = {"mono","stereo"};


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

/* VP_Output and VP_OutputSeek are not needed when calling VP_GetInfo() */
void VP_Output () { return; }
void VP_OutputSeek () { return; }



/*
 * MAIN
 */

void main (int argc, char *argv[])
{
 long Len;		/* compressed file length */
 VP_Info Info;		/* structure that receives the information requested */


 /* check command-line parameters */
 if (argc != 2) {
    puts("\nUsage:  INFO <source>");
    return; }

 /* open source file */
 if ( (In = fopen(argv[1], "rb")) == NULL ) {
    printf("\nFile not found %s\n", argv[1]);
    return; }

 /* detect source file content */
 switch (VP_GetInfo(&Info)) {		/* get info in Info */
	case VP_OK:
		break;			/* ok, Vocpack 2.0 */

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

 /* get compressed file length and close it */
 fseek(In, 0, SEEK_END);
 Len = ftell(In);
 fclose(In);

 /* write description */
 printf("\n%s is compressed with Vocpack, method 2.0\n\n", argv[1]);
 printf("Original name: %s\n", Info.Name);

 printf("File type: %s %s %s", WriteSize[Info.Is16Bit],
	WriteSign[Info.IsSigned], WriteStereo[Info.IsStereo]);
 if (Info.Align) printf(", alignment = %d", Info.Align);

 printf("\n\nUnpacked length =%8ld bytes\n", Info.UnpackedLen);
 printf("Packed length   =%8ld bytes\n", Len);
 printf("Ratio = %02d%%\n", (int)((Len*100l) / Info.UnpackedLen));
}
