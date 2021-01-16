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

#define DEXMAGIC_VERSION "1.0.0"

#define MAX_FILE_SIZE 50000000	// 50BM or 50,000,000 bytes

static void usage(void)
{
	fprintf(stderr,
			"dexmagic %s\n"
			"Runs some custom checks and produces a magic result\n"
			"\n"
			"Usage: dexmagic <input>\n"
			"  -h, --help              Output this help and exit\n"
			"  -V, --version           Output version and exit\n"
			"\n", DEXMAGIC_VERSION);
	exit(EXIT_FAILURE);
}

char * inputFilePath=0;

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
		else if(!strcmp(argv[i],"-V") || !strcmp(argv[i], "--version"))
		{
			printf("dexmagic %s\n", DEXMAGIC_VERSION);
			exit(EXIT_SUCCESS);
		}
		else
		{
			break;
		}
	}

	argc -= i;
	argv += i;

	if(argc<1)
		usage();

	inputFilePath = argv[0];
}

const char * checkASCII(uint8_t * data, off_t size)
{
	for(off_t i=0;i<size;i++)
	{
		uint8_t c = data[i];
		if((c!=9 && c!=10 && c!=13 && (c<32 || c>126)))
			return 0;
	}

	return "Printable ASCII";
}

const char * checkNullBytes(uint8_t * data, off_t size)
{
	for(off_t i=0;i<size;i++)
	{
		uint8_t c = data[i];
		if(c!=0)
			return 0;
	}

	return "All Null Bytes";
}

const char * checkIdenticalBytes(uint8_t * data, off_t size)
{
	uint8_t last = 0;
	for(off_t i=0;i<size;i++)
	{
		uint8_t c = data[i];
		if(i>0 && c!=last)
			return 0;
		last = c;
	}

	return "All Identical Bytes";
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

	const char * result = 0;
	if((result = checkASCII(data, s.st_size)))
		printf("%s\n", result);
	if((result = checkNullBytes(data, s.st_size)))
		printf("%s\n", result);
	if((result = checkIdenticalBytes(data, s.st_size)))
		printf("%s\n", result);

	cleanup:
	if(data>0)
		munmap(data, s.st_size);
	if(infd>=0)
		close(infd);
	if(outfd>=0)
		close(outfd);

	exit(EXIT_SUCCESS);
}
