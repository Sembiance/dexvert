
#define  BUFSIZE 32000
#define  MAXFILES  400
#define  TRIES      16
#define  DELAY       2
#define  TRUE        1
#define  FALSE       0

#include <stdio.h>
#include <dos.h>
#include <io.h>
#include <string.h>
#include <fcntl.h>
#include <dir.h>
#include <process.h>
#include <stdlib.h>
#include <alloc.h>
#include <mem.h>

extern  unsigned char   _osmajor;

void    fattenfile(char *);
void    getbuffer(void);
char    *filefind(void);
int     int24handler(int, int, int, int);
int     isnet(void);

/***************************************************************/

int     fhin, fhout;
char    *buffer;
int     bytecount;

double  oldsize, newsize;
double  skinny_pct;

char    *filename_ptr;
char    msg[25];
char    *footprint;
char    *filepattern;
char    foottest[80];

struct  ffblk   dos_find_blk;

char    *filename_array;
char    *name_ptrs[MAXFILES];

char    drive[MAXDRIVE];
char    dirs[MAXDIR];
char    filename[MAXFILE];
char    ext[MAXEXT];
int     name_flag;

int     count, error, mode, fileattrib, driveno;
int     network, exists;
int     numfiles;
int     firsttime;

char    drive[MAXDRIVE];
char    dirs[MAXDIR];
char    filename[MAXFILE];
char    ext[MAXEXT];
int     name_flag;

int     i, j, k;
int     argcx, argdx;
long    filetime;

char far    *mydta;
char far    *olddta;
unsigned    useg;
unsigned    int our_cs;

/***************************************************************/

void    main (argc, argv, envp)
                int     argc;
                char    *argv[];
                char    *envp[];

        {
        harderr(int24handler);

        count = 0;

        _AX = 0x3341;
        geninterrupt(0x21);
        if (_DX == 0x1234)
            goto loaded_ok;

        printf("\n\nPlease run Diet Disk before trying to fatten files.\n\n");
        exit(1);


loaded_ok:
        if (argc != 2)
           {
           printf("\n\nUsage: FATTEN <filename>.  Wildcards are * and ?.\n\n");
           exit(0);
           }

        name_flag = fnsplit(argv[1], drive, dirs, filename, ext);
        filepattern = argv[1];

        if (_osmajor < 2)
           {
           printf("\n\nIncorrect DOS version.\n\n");
           goto bail_out;
           }

        if ((buffer = (char *) malloc(BUFSIZE)) == NULL)
           {
           printf("\n\nInsufficient memory.\n\n");
           goto bail_out;
           }

        if ((filename_array = (char *) calloc(MAXFILES, 14)) == NULL)
           {
           printf("\n\nInsufficient memory.\n\n");
           goto bail_out;
           }


        if ((mydta = (char *) malloc(128)) == NULL)
           {
           printf("\n\nInsufficient memory.\n\n");
           goto bail_out;
           }


        _fmode  = O_BINARY;
        error   = 0;
        mode    = O_RDONLY;
        network = 0;

        if (isnet())
           {
           network = 1;
           mode    = O_RDONLY | O_DENYNONE;
           argdx   = TRIES;
           argcx   = DELAY;
           ioctl (0, 11, argdx, argcx);
           }

        numfiles = 0;
        bytecount = 0;

        while ( (filename_ptr = filefind()) != NULL)
            {
            name_ptrs[numfiles] = filename_array + bytecount;
            movmem(filename_ptr,  filename_array + bytecount,
                        strlen(filename_ptr)+1);
            bytecount += (strlen(filename_ptr)+1);
            numfiles++;
            if (numfiles > (MAXFILES - 5))
                {
                printf("\nToo many files (max is 400).\n");
                printf("Change your wildcards to fatten fewer files at a time.\n");
                goto bail_out;
                }
            }

        if (numfiles == 0)
           {
           printf("\nFile(s) not found.\n");
           goto bail_out;
           }

        printf("Fattening files....\n\n");

        for (i = 0; i < numfiles; i++)
            fattenfile(name_ptrs[i]);
        

normal_exit:
        printf("\n%d file(s) fattened.\n", count);

        if (error)
            {
            printf("Fatten ended.  Some errors occurred.\n");
            exit(1);
            }

        printf("\n\nFatten ended successfully.\n");
        exit(0);


bail_out:
        fcloseall();
        printf("\n%d file(s) fattened.\n", count);
        printf("Fatten ended due to error.\n");
        exit(1);
        }

/***************************************************************/

void    fattenfile(char *cptr)

        {
        char    iptr[MAXPATH];
        char    optr[MAXPATH];
        struct  ftime ftimestruc;
        char    fullname[MAXPATH];


        strcpy(iptr, cptr);
        strupr(iptr);
        printf("  %-14s ", iptr);

        fnmerge(fullname, drive, dirs, iptr, NULL);
        strcpy(iptr, fullname);
        fnmerge(optr, drive, dirs, "TEMP", ".FAT");

        if (strstr("TEMP.FAT", iptr) != NULL)
           {
           printf("\nInvalid file name!\n");
           error = 1;
           return;
           }

        if (strstr(optr, iptr) != NULL)
           {
           printf("\nInvalid file name!\n");
           error = 1;
           return;
           }

        if ((fhin = _open(iptr, mode)) == -1)
           {
           printf("\nInternal error; file not found.\n");
           exit(1);
           }

        if ((fhout = _creat(optr, 0)) == -1)
           {
           printf("\nInternal error--file creation.\n");
           exit(1);
           }

        getbuffer();
        while (bytecount > 0)
              {
              if ((_write(fhout, buffer, bytecount)) != bytecount)
                 {
                 printf("\nError writing file.");
                 printf("\nFatten operation terminated.\n");
                 remove (optr);
                 exit(1);
                 }

              if (bytecount < BUFSIZE)
                 break;

              getbuffer();
              }

        getftime(fhin, &ftimestruc);
        setftime(fhout,&ftimestruc);

        _close (fhin);
        _close (fhout);

        findfirst(iptr, (struct ffblk *) &dos_find_blk, 0);
        oldsize   = dos_find_blk.ff_fsize * 1.0;

        findfirst(optr, (struct ffblk *) &dos_find_blk, 0);
        newsize   = dos_find_blk.ff_fsize * 1.0;

        if (oldsize != newsize)
            {
            printf ("old size = %10.0lf  new size = %10.0lf  ", oldsize, newsize);
            if (newsize == 0.0)
               skinny_pct = 0.0;
            else
               skinny_pct = ((newsize - oldsize) / newsize) * 100.0;
            printf(" (% 4.0lf%%)\n", skinny_pct);
            remove (iptr);
            rename (optr, iptr);
            count++;
            }
        else
            {
            printf (" ...was already fat.\n");
            remove (iptr);
            rename (optr, iptr);
            }
        }

/***************************************************************/

void    getbuffer()

        {
        if ((bytecount = _read(fhin, buffer, BUFSIZE)) == -1)
           {
           printf("\nError reading file.");
           printf("\nFatten operation terminated.\n");
           exit(1);
           }
        }

/***************************************************************/

char    *filefind()
        {

        olddta = getdta();

        if (firsttime) goto getnextblk;

        firsttime = 1;
        if (findfirst(filepattern, (struct ffblk *) &dos_find_blk, 0) != 0)
           {
            setdta( (char far *) &olddta);
            return(NULL);
           }

        setdta( (char far *) &olddta);
        return(dos_find_blk.ff_name);

getnextblk:
        if (findnext( (struct ffblk *) &dos_find_blk) != 0)
           {
            setdta( (char far *) &olddta);
            return(NULL);
           }

        setdta( (char far *) &olddta);
        return(dos_find_blk.ff_name);

        }

/***************************************************************/

int     isnet()
        {
        union REGS      regs;

        if (_osmajor > 2 && _osminor > 0)
            for (i=3; i<21; i++)
                {
                regs.x.ax = 0x4409;
                regs.x.bx = i;
                int86(0x21, &regs, &regs);
                if ( (regs.x.dx & 0x1000) == 0x1000 )
                    return(TRUE);
                }
        return(FALSE);
        }

/***************************************************************/

int     int24handler(int errval, int ax, int bp, int si)

        {
        char    msg[25];
        int     drive;

        if (ax < 0)
            {
            bdosptr(0x09, "\nDevice I/O error has occurred.\n$", 0);
            bdosptr(0x09, "Attempting to recover....\n$", 0);
            hardretn(-1);
            }

        drive = (ax & 0x00FF);
        sprintf(msg, "I/O error on disk drive %c. \n$", 'A' + drive);
        bdosptr(0x09, msg, 0);
        bdosptr(0x09, "Attempting to recover....\n$", 0);
        hardretn(-1);
        }

/***************************************************************/


