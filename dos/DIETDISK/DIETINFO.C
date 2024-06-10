
#include <stdio.h>
#include <dos.h>
#include <fcntl.h>
#include <io.h>
#include <conio.h>
#include <string.h>
#include <dir.h>
#include <stdlib.h>

char    *filefind(char *filepat);
int     int24handler(int, int, int, int);
void    display_stats(void);
void    do_heading(void);

/***************************************************************/

int         firsttime;
int         filehandle;
int         filecount;
int         linecount;

double      actual_size;
double      pretend_size;
double      total_actual;
double      total_pretend;
char        yes_no [4];
double      percent;

char far    *olddta;
char        drive[MAXDRIVE];
char        dirs[MAXDIR];
char        filename[MAXFILE];
char        ext[MAXEXT];
char        fullname[MAXPATH];
char        filepat [MAXPATH];
char        *foundname;
char        *opt1;
char        *opt2;
char        *filename_ptr;

struct      ftime   ftimestruc;
struct      ffblk   dos_find_blk;

unsigned    int useg;
unsigned    int our_cs;
char        *footprint;
char        foottest[80];

unsigned int diet_cs = 0;
int far     *diet_flag_ptr;

char    fs_loaded = 0;
int     bytes;

struct  {
        char  signature[6];
        long  filesize;
        char  filler[6];
        }
        ctlrec;

/***************************************************************/

void    main(int argc, char *argv[])
        {
        harderr(int24handler);
        fs_loaded = 0;

        _AX = 0x3341;
        geninterrupt(0x21);
        if (_DX == 0x1234)
            diet_cs = _CX;

        if (diet_cs != 0)
            {
            fs_loaded = 1;
            diet_flag_ptr = MK_FP(diet_cs, 0x0103);
            }

        if (argc == 2)
            {
            strcpy (filepat, argv[1]);
            }
        else
            {
            strcpy (filepat, "*.*");
            }


        filecount = 0;
        linecount = 0;
        fnsplit(filepat, drive, dirs, filename, ext);

        do_heading();

        while ( (foundname = filefind(filepat)) != NULL )
            {
            fnmerge(fullname, drive, dirs, foundname, NULL);
            if ((filehandle = _open(fullname, O_RDWR)) == -1)
               {
               printf("Internal error; file not found.\n");
               exit(1);
               }

            actual_size  = (double) dos_find_blk.ff_fsize;

            if (fs_loaded)
                pretend_size = (double) filelength(filehandle);
            else
                {
                bytes = read(filehandle, &ctlrec, 16);
                if (bytes != 16)
                    pretend_size = actual_size;
                else
                if (memcmp(ctlrec.signature, "lZdIeT", 6) != 0)
                    pretend_size = actual_size;
                else
                    pretend_size = (double) ctlrec.filesize;
                }
            filecount++;
            display_stats();

            _close (filehandle);
            }

        if (total_pretend == 0.0)
           percent = 0.0;
        else
           percent = ((total_pretend - total_actual) / total_pretend) * 100.0;

        printf(
        "%9.0lf bytes in %d files; %8.0lf bytes saved.  (%4.0lf%%)\n",
        total_actual, filecount, total_pretend - total_actual, percent);
        }

/***************************************************************/

void    display_stats(void)
        {
        if (linecount > 23)
            {
            linecount = 0;
            printf("Press any key to continue the list....\n");
            getch();
            do_heading();
            }

        if (pretend_size == 0.0)
           percent = 0.0;
        else
           percent = ((pretend_size - actual_size) / pretend_size) * 100.0;

        if (actual_size == pretend_size)
            strcpy(yes_no, " No");
        else
            strcpy(yes_no, "Yes");

        total_actual  += actual_size;
        total_pretend += pretend_size;

        printf(
"%-12s        %-3s      %8.0lf          %8.0lf         % 4.0lf%%\n",
foundname, yes_no, actual_size, pretend_size, percent);
        linecount++;

        }

/***************************************************************/

void    do_heading(void)
        {
        if (fs_loaded)
            {
            if (*diet_flag_ptr == 0)
                printf("Diet Disk is active.\n");
            else
                printf("Diet Disk is loaded but not active.\n");
            }
        else
            printf("Diet Disk is not loaded.\n");

        printf(
"File              Skinny?     File Size       Unskinny Size      Percent\n");
        printf(
"-------------     -------     ---------       -------------      -------\n");
        linecount += 3;
        }

/***************************************************************/

char    *filefind(char *filepat)
        {

        olddta = getdta();

        if (firsttime) goto getnextblk;

        firsttime = 1;
        if (findfirst(filepat, (struct ffblk *) &dos_find_blk, 0) != 0)
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




