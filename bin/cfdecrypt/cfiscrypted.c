/* CFISCRYPTED: Checks to see if stdin is a template encrypted with CFCRYPT


Matt Chapman <matthewc@cse.unsw.edu.au>

Usage: cfdecrypt <encrypted.cfm >decrypted.cfm

Requires a DES encryption library to compile.

Compile:
Put this file in ~/openssl_ver/crypto/des
 
~/openssl-1.0.0d/crypto/des> gcc -static ~/openssl-1.0.0d/crypto/des/des_old.c -lcrypto ~/openssl-1.0.0d/crypto/des/cfdecrypt.c -o cfdecrypt

*/

#include <stdio.h>
//#include "des.h"

int main(void)
{
	char *header = "Allaire Cold Fusion Template\012Header Size: ";
	char buffer[54];
	int debug = 0;
	int headsize, outlen, seek_pos;
	//int skip_header;
	//int len, i;
	
	/* Note: This IS the encryption key! It is meant to look like an error. */
	//char *keystr = "Error: cannot open template file--\"%s\". Please, try again!\012\012"; 
	
	/*des_cblock key;
	des_cblock input;
	des_cblock output;
	des_key_schedule schedule;
	*/
	if ((fread(buffer, 1, 54, stdin) < 54) || (memcmp(buffer, header, 42)))
	{
		if(debug) fprintf(stderr, "File is not an encrypted template\n");
		return 1;
	}

	if (!memcmp(&buffer[42], "New Version", 11))
	{
		if(debug) fprintf(stderr, "\nEncrypted with 'New Version'\n");
		headsize = 69;
		//skip_header = 1;
	}
	else
	{
		if(debug) fprintf(stderr, "\nEncrypted with 'Old Version'\n");
		headsize = atoi(&buffer[42]);
		//skip_header = 0;
	}
	
	seek_pos = fseek(stdin, headsize, SEEK_SET);
	if ((headsize < 54) || seek_pos < 0)
	{
		if(debug){ 
			fprintf(stderr, "Error in file format.\n Head size: %i\n",headsize);		
			if (headsize < 54){ fprintf(stderr, "Error: Head Size < 54");}
			if (seek_pos < 0){  fprintf(stderr, "Couldn't set seek position: %i",seek_pos);}
			fprintf(stderr, "\n");
		}
		return 1;
	}
	return 0;
}
