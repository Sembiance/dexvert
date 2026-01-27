#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    if(argc!=4)
    {
        fprintf(stderr, "Usage: %s <input> <output> <xor_key_hex>\n", argv[0]);
        return 1;
    }

    FILE *in = fopen(argv[1], "rb");
    FILE *out = fopen(argv[2], "wb");
    unsigned char key = (unsigned char)strtol(argv[3], NULL, 16);

    int c;
    while ((c = fgetc(in)) != EOF)
        fputc(c ^ key, out);

    fclose(in);
    fclose(out);

    return 0;
}
