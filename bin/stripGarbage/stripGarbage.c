#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <fcntl.h>
#include <signal.h>
#include <string.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>

#define STRIP_GARBAGE_VERSION "1.1.0"

#define MAX_FILE_SIZE 50000000	// 50BM or 50,000,000 bytes

static void usage(void)
{
	fprintf(stderr,
			"stripGarbage %s\n"
			"Strips all 0x00 and 0x1A bytes from a file.\n"
			"\n"
			"Usage: stripGarbage <input> <output>\n"
			"  -h, --help              Output this help and exit\n"
			"  -V, --version           Output version and exit\n"
			"  -n, --null              Only strip null bytes\n"
			"  -a, --ascii             Only strip if the rest of the file is ASCII\n"
			"\n", STRIP_GARBAGE_VERSION);
	exit(EXIT_FAILURE);
}

char * inputFilePath=0;
char * outputFilePath=0;
bool ascii=false;
bool nullOnly=false;

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
		else if(!strcmp(argv[i],"-n") || !strcmp(argv[i], "--null"))
		{
			nullOnly = true;
		}
		else if(!strcmp(argv[i],"-V") || !strcmp(argv[i], "--version"))
		{
			printf("stripGarbage %s\n", STRIP_GARBAGE_VERSION);
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
	uint8_t * data=0;
	struct stat s;

	parse_options(argc, argv);

	if(stat(inputFilePath, &s)==-1)
	{
		fprintf(stderr, "Failed to stat [%s]: %s\n", inputFilePath, strerror(errno));
		goto cleanup;
	}

	if(s.st_size==0)
	{
		fprintf(stderr, "Input file [%s] is zero bytes long\n", inputFilePath);
		goto cleanup;
	}
	
	if(s.st_size>MAX_FILE_SIZE)
	{
		fprintf(stderr, "File size of %ld bytes larger than max of %u bytes\n", s.st_size, MAX_FILE_SIZE);
		goto cleanup;
	}

	infd = open(inputFilePath, O_RDONLY);
	if(infd==-1)
	{
		fprintf(stderr, "Failed to open input file [%s]: %s\n", inputFilePath, strerror(errno));
		goto cleanup;
	}
	
	data = mmap(0, s.st_size, PROT_READ, MAP_PRIVATE, infd, 0);
	if((void *)data==MAP_FAILED)
	{
		fprintf(stderr, "Failed to mmap input file [%s]: %s\n", inputFilePath, strerror(errno));
		goto cleanup;
	}
	
	outfd = open(outputFilePath, O_CREAT | O_WRONLY, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
	if(outfd==-1)
	{
		fprintf(stderr, "Failed to open output file [%s]: %s\n", outputFilePath, strerror(errno));
		goto cleanup;
	}

	off_t stripCount = 0;
	for(off_t i=0;i<s.st_size;i++)
	{
		uint8_t c = data[i];
		if((!nullOnly && c==26) || c==0)
		{
			stripCount++;
			continue;
		}

		if(ascii && (c!=9 && c!=10 && c!=13 && (c<32 || c>126)))
		{
			fprintf(stderr, "Invalid binary character detected 0x%x (%d) at offset %ld\n", c, c, i);
			goto cleanupWithDelete;
		}

		if(write(outfd, &c, 1)!=1)
		{
			fprintf(stderr, "Failed to write output byte 0x%x (%d) at offset %ld: %s\n", c, c, i, strerror(errno));
			goto cleanupWithDelete;
		}
	}

	if(stripCount==0)
	{
		fprintf(stderr, "No garbage characters detected.\n");
		goto cleanupWithDelete;
	}

	goto cleanup;

	cleanupWithDelete:
	close(outfd);
	outfd = 0;
	unlink(outputFilePath);

	cleanup:
	if(data>0)
		munmap(data, s.st_size);
	if(infd>=0)
		close(infd);
	if(outfd>=0)
		close(outfd);

	exit(EXIT_SUCCESS);
}
