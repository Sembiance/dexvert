/* CFDECRYPT: Decrypt Cold Fusion templates encrypted with CFCRYPT
   Matt Chapman <matthewc@cse.unsw.edu.au>

   Requires libdes to compile.
*/

#include <stdlib.h>
#include <stdio.h>
#include "des.h"

int main(int argc, char *argv[])
{
	FILE *infile, *outfile;

	char *header = "Allaire Cold Fusion Template\012Header Size: ";
	char buffer[54];
	int headsize, outlen;
	int skip_header;
	int len, i;

	char *keystr = "Error: cannot open template file--\"%s\". Please, try again!\012\012";
	des_cblock key;
	des_cblock input; 
	des_cblock output;
	des_key_schedule schedule;

	switch (argc)
	{
	case 2:
		outfile = stdout;
		break;

	case 3:
		if (!(outfile = fopen(argv[2], "wb")))
		{
			fprintf(stderr, "Error opening output file %s\n", argv[2]);
			return 1;
		}
		break;

	default:
		fprintf(stderr, "Usage: cfdecrypt <encrypted template> [output file]\n");
		return 1;
	}

	if (!(infile = fopen(argv[1], "rb")))
	{
		fprintf(stderr, "Error opening input file %s\n", argv[1]);
		return 1;
	}

	if ((fread(buffer, 1, 54, infile) < 54) || (memcmp(buffer, header, 42)))
	{
		fprintf(stderr, "File is not an encrypted template\n");
		return 1;
	}

	if (!memcmp(&buffer[42], "New Version", 11))
	{
		headsize = 69;
		skip_header = 1;
	}
	else
	{
		headsize = atoi(&buffer[42]);
		skip_header = 0;
	}

	if ((headsize < 54) || (fseek(infile, headsize, SEEK_SET) < 0))
	{
		fprintf(stderr, "Error in file format\n");
		return 1;
	}

	des_string_to_key(keystr, &key);
	des_set_key(&key, schedule);
	outlen = 0;

	while ((len = fread(input, 1, 8, infile)) == 8)
	{
		des_ecb_encrypt(&input, &output, schedule, 0);
		outlen += 8;
		i = 0;

		if (skip_header)
		{
			while (i < 8)
			{
				if (output[i++] == 0x1A)
				{
					skip_header = 0;
					break;
				}
			}
		}

		fwrite(output + i, 1, 8 - i, outfile);
	}

	for (i = 0; i < len; i++)
	{
		output[i] = input[i] ^ (outlen + i);
	}

	fwrite(output, 1, len, outfile);

	fclose(outfile);
	fclose(infile);
	return 0;
}
