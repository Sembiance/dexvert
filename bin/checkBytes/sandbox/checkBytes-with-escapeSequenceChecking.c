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

#define CHECKBYTES_VERSION "1.1.0"

#define MAX_FILE_SIZE 50000000	// 50BM or 50,000,000 bytes

static void usage(void)
{
	fprintf(stderr,
			"checkBytes %s\n"
			"Runs some checks on the bytes in a file and prints a result\n"
			"\n"
			"Usage: checkBytes <input>\n"
			"  -h, --help              Output this help and exit\n"
			"  -V, --version           Output version and exit\n"
			"\n", CHECKBYTES_VERSION);
	exit(EXIT_FAILURE);
}

char * inputFilePath=0;

static void parse_options(int argc, char **argv)
{
	int i;

	for(i=1;i<argc;i++)
	{
		//int lastarg = i==argc-1;

		if(!strcmp(argv[i],"-h") || !strcmp(argv[i], "--help"))
		{
			usage();
		}
		else if(!strcmp(argv[i],"-V") || !strcmp(argv[i], "--version"))
		{
			printf("checkBytes %s\n", CHECKBYTES_VERSION);
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

struct dataState
{
	uint8_t * data;
	off_t i;
	off_t size;
};

int nextChar(struct dataState * state)
{
	if(state->i==state->size)
		return EOF;

	int c = state->data[state->i];
	state->i++;	
	return c;
}

off_t checkEscapeSequence(uint8_t * data, off_t start, off_t size)
{
	off_t count=0;

	off_t i = start;
	uint8_t c = data[++i];

	// logic derived from: https://en.wikipedia.org/wiki/ANSI_escape_code

	// CSI (Control Sequence Introducer)
	if(c=='[')
	{
		//    parameter bytes: 0 or more bytes from 0x30 '0' to 0x3F '?'
		for(i++;i<size && data[i]>='0' && data[i]<='?';i++);
		
		// intermediate bytes: 0 or more bytes from 0x20 ' ' to 0x2F '/'
		for(;i<size && data[i]>=' ' && data[i]<='/';i++);
		
		//         final byte:   a single byte from 0x40 '@' to 0x7E '~'
		c = data[i];
		if(c<'@' || c>'~')
			return 0;
		
		return i-start;
	}
	else if(c==']')
	{
		// TODO add support
		return 0;
	}

	return 0;
}

const char * checkData(uint8_t * data, off_t size)
{
	bool printableASCII=true;
	bool allNull=true;
	bool allIdentical=true;
	bool alternatingNull=true;
	uint8_t last=0;
	bool null=data[0]==0;
	bool trailNull=false;
	uint32_t escapeSequenceCount=0;

	for(off_t i=0;i<size;i++)
	{
		uint8_t c = data[i];

		if(c==27)
		{
			allNull = false;
			
			off_t escapeLength = checkEscapeSequence(data, i, size);
			if(escapeLength)
			{
				printf("got escape length %lu at offset %lu\n", escapeLength, i);
				alternatingNull = false;
				allIdentical = false;

				i+=escapeLength;
				continue;
			}
		}
		
		if(printableASCII && (c!=7 && c!=8 && c!=9 && c!=10 && c!=13 && (c<32 || c>126)))	// 7 (bell) and 8 (backspace) are not normally printable, but exists in ANSI files from the day
			printableASCII = false;

		if(allNull && c!=0)
			allNull = false;

		if(i>0 && allIdentical && c!=last)
			allIdentical = false;
		else if(allIdentical)
			last = c;
		
		if(i>0 && alternatingNull)
		{
			if(c!=0)	// not null
			{
				// if we expecting all trailing nulls, return false
				if(trailNull)
					alternatingNull = false;
				
				// if previous wasn't null, return false
				if(!null)
					alternatingNull = false;
			}
			else	// null
			{
				// if previous was null too, we might be in trailing null section, mark and continue
				if(!trailNull && null)
					trailNull = true;
			}
			
			null = !null;
		}

		if(!printableASCII && !allNull && !allIdentical && !alternatingNull)
			break;
	}

	if(printableASCII)		// if we are ascii we can't be any of the below
		return "Printable ASCII";
	if(allNull)	// if we are all null, we don't need to output we are identical, nor can we be alternating
		return "All Null Bytes";
	if(allIdentical)	// if we are identical, we can't be alternating
		return "All Identical Bytes";
	if(alternatingNull)
		return "Null Bytes Alternating";
	
	return NULL;
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

	const char * result = checkData(data, s.st_size);
	if(result)
		printf("%s\n", result);

	cleanup:
	if(data!=0)
		munmap(data, s.st_size);
	if(infd>=0)
		close(infd);
	if(outfd>=0)
		close(outfd);

	exit(EXIT_SUCCESS);
}
