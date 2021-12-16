#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <fcntl.h>
#include <signal.h>
#include <string.h>
#include <sys/types.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>

#define TRIM_GARBAGE_VERSION "1.1.0"

static void usage(void)
{
	fprintf(stderr,
			"trimGarbage %s\n"
			"Trims all trailing 0x00 and 0x1A bytes from a file.\n"
			"\n"
			"Usage: trimGarbage <input> <output>\n"
			"  -n, --newlines          Also trim newlines\n"
			"  -h, --help              Output this help and exit\n"
			"  -V, --version           Output version and exit\n"
			"  -a, --ascii             Only trim if the rest of the file is ASCII\n"
			"\n", TRIM_GARBAGE_VERSION);
	exit(EXIT_FAILURE);
}

bool ascii=false;
bool newlines=false;
char * inputFilePath=0;
char * outputFilePath=0;

static void parse_options(int argc, char **argv)
{
	int i;

	for(i=1;i<argc;i++)
	{
		int lastarg = i==argc-1;

		if(!strcmp(argv[i],"-h") || !strcmp(argv[i], "--help"))
		{
			usage();
		}
		else if(!strcmp(argv[i],"-a") || !strcmp(argv[i], "--ascii"))
		{
			ascii = true;
		}
		else if(!strcmp(argv[i],"-n") || !strcmp(argv[i], "--newlines"))
		{
			newlines = true;
		}
		else if(!strcmp(argv[i],"-V") || !strcmp(argv[i], "--version"))
		{
			printf("trimGarbage %s\n", TRIM_GARBAGE_VERSION);
			exit(EXIT_SUCCESS);
		}
		else
		{
			break;
		}
	}

	argc -= i;
	argv += i;

	if(argc<2)
		usage();

	inputFilePath = argv[0];
	outputFilePath = argv[1];
}

int main(int argc, char ** argv)
{
	int infd=-1;
	int outfd=-1;

	parse_options(argc, argv);

	struct stat s;
	if(stat(inputFilePath, &s)==-1)
	{
		fprintf(stderr, "Failed to stat input file: %s\n", inputFilePath);
		goto finish;
	}

	if(s.st_size==0)
	{
		fprintf(stderr, "Input file [%s] is zero bytes long\n", inputFilePath);
		goto finish;
	}

	infd = open(inputFilePath, O_RDONLY);
	if(infd==-1)
	{
		fprintf(stderr, "Failed to open input file [%s]: %s\n", inputFilePath, strerror(errno));
		goto finish;
	}
	
	uint8_t c;
	uint8_t tcount = 0;
	bool tdone=false;
	for(off_t i=1;i<s.st_size;i++)
	{
		if(lseek(infd, -i, SEEK_END)==-1)
		{
			fprintf(stderr, "Failed to SEEK_END to byte offset %ld in file [%s]: %s\n", i, inputFilePath, strerror(errno));
			goto finish;
		}

		if(read(infd, &c, 1)==-1)
		{
			fprintf(stderr, "Failed to read byte from inputFile [%s]: %s\n", inputFilePath, strerror(errno));
			goto finish;
		}

		if(!tdone)
		{
			if(c==26 || c==0 || (newlines && (c==13 || c==10)))
			{
				tcount++;
				continue;
			}

			if(tcount==0)
			{
				fprintf(stderr, "Input file [%s] does not end with the required bytes. Encountered %d\n", inputFilePath, c);
				goto finish;
			}
			
			tdone = true;
		}

		if(!ascii)
			break;
		
		if(c!=9 && c!=10 && c!=13 && (c<32 || c>126))
		{
			fprintf(stderr, "Encountered non-ascii byte 0x%x (%d) in input file [%s]\n", c, c, inputFilePath);
			goto finish;
		}
	}

	lseek(infd, 0, SEEK_SET);

	outfd = open(outputFilePath, O_CREAT | O_WRONLY, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
	if(outfd==-1)
	{
		fprintf(stderr, "Failed to open output file [%s]: %s\n", outputFilePath, strerror(errno));
		goto finish;
	}

	for(size_t outsize=s.st_size-tcount;outsize>0;)
	{
		ssize_t sent = sendfile(outfd, infd, 0, outsize);
		if(sent<=0)
		{
			fprintf(stderr, "Failed to sendfile to output file [%s]: %s\n", outputFilePath, strerror(errno));
			goto finish;
		}
		outsize-=sent;
	}

	finish:
	if(infd>=0)
		close(infd);
	if(outfd>=0)
		close(outfd);

	exit(EXIT_SUCCESS);
}
