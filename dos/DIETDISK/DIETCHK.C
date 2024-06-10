
#include <stdio.h>
#include <dos.h>
#include <dir.h>
#include <io.h>
#include <fcntl.h>
#include <string.h>

#define  FALSE   0
#define  TRUE    1

int     critical_error;
void    interrupt (*oldint24)(void);
char    diet_id[] = "lZdIeT";
int     i, filecount, flag;
int     bytes_read;
int     error_flag;
int     fixit;
unsigned char *status_ptr;
struct  ffblk fblock;
char    drive[5];
char    path[81];
char    name[10];
char    ext[5];

char    segment_rec[4000];

struct  {
        char    signature[6];
        long    filelen;
        char    filler[6];
        }
        footprint;

struct  {
        long    next_ctl;
        long    prev_ctl;
        char    filler[8];
        struct  {
                long  location;
                int   length;
                }
                location_length[250];
        }
        control_rec;

/* -------------------------------------------------- */

void    interrupt int24(unsigned bp, unsigned di, unsigned si,
                        unsigned ds, unsigned es, unsigned dx,
                        unsigned cx, unsigned bx, unsigned ax,
                        unsigned ip, unsigned cs, unsigned flags)
        {
        critical_error = TRUE;
        ax = (ax & 0xFF00) | 0x03;
        }

void    check_file(void)
        {
        char    fullname[101];
        unsigned char next_byte;
        long    actual_size;
        long    ctl_file_position;
        int     handle;
        int     ctl_rec_counter;
        int     corrected;

        critical_error = FALSE;
        fnmerge(fullname, drive, path, fblock.ff_name, "");
        actual_size = fblock.ff_fsize;

        if (!fixit)
            handle = _open(fullname, O_RDONLY | O_BINARY);
        else
            handle = _open(fullname, O_RDWR   | O_BINARY);

        if (handle == -1)
            {
            printf("Error opening %s\n", fblock.ff_name);
            return;
            }
        bytes_read = read(handle, &footprint, sizeof(footprint));
        if (bytes_read != sizeof(footprint))
            {
            _close(handle);
            return;
            }
        if (memcmp(&footprint.signature, diet_id, 6) != 0)
            {
            _close(handle);
            return;
            }

        filecount++;
        printf("File %s -- actual size: %ld      fattened size: %ld\n",
                fblock.ff_name, actual_size, footprint.filelen);
        ctl_rec_counter = 0;

process_control:
        corrected = FALSE;
        ctl_rec_counter++;
        ctl_file_position = tell(handle);
        bytes_read = read(handle, &control_rec, sizeof(control_rec));
        if (bytes_read != sizeof(control_rec))
            {
            error_flag = TRUE;
            printf("Error in ctrl rec %d in %s\n",
                    ctl_rec_counter, fblock.ff_name);
            if (critical_error)
                printf("Critical I/O error occurred.\n");
            else
            if (bytes_read >= 0)
                printf("%d bytes requested; %d were read.\n",
                    (int) sizeof(control_rec), bytes_read);
            else
                printf("Permission denied.\n");
            _close(handle);
            return;
            }

        status_ptr = (unsigned char *) &control_rec;
        status_ptr += 127;
        next_byte = (unsigned char) *status_ptr;
        status_ptr--;
        if (*status_ptr != 0 && *status_ptr != 0xff)
            {
            printf("Status byte error in ctrl rec %d in %s\n",
                    ctl_rec_counter, fblock.ff_name);
            error_flag  = TRUE;
            corrected   = TRUE;
            *status_ptr = next_byte;
            }

        for (i=0; i<250; i++)
            {
            if (control_rec.location_length[i].location > 1024000l)
                {
                error_flag = TRUE;
                printf("Ctl rec %d; segment %d error in %s (loc. out of bounds)\n",
                            ctl_rec_counter, i, fblock.ff_name);
                control_rec.location_length[i].location = -1;
                control_rec.location_length[i].length   = -1;
                corrected = TRUE;
                continue;
                }
            if (control_rec.location_length[i].length != -1)
                {
                if (control_rec.location_length[i].length > 2048 + 256)
                    {
                    error_flag = TRUE;
                    printf("Ctl rec %d; segment %d error in %s\n",
                                ctl_rec_counter, i, fblock.ff_name);
                    printf("%d bytes (too large)\n",
                        control_rec.location_length[i].length);
                    control_rec.location_length[i].location = -1;
                    control_rec.location_length[i].length   = -1;
                    corrected = TRUE;
                    continue;
                    }
                critical_error = FALSE;
                lseek(handle, control_rec.location_length[i].location, 0);
                bytes_read = read(handle, segment_rec,
                                  control_rec.location_length[i].length);
                if (bytes_read != control_rec.location_length[i].length)
                    {
                    error_flag = TRUE;
                    printf("Ctl rec %d; segment %d error in %s\n",
                                ctl_rec_counter, i, fblock.ff_name);
                    if (critical_error)
                        printf("Critical I/O error occurred.\n");
                    else
                    if (bytes_read >= 0)
                        {
                        printf("%d bytes requested; %d were read.\n",
                            control_rec.location_length[i].length,
                            bytes_read);
                        control_rec.location_length[i].location = -1;
                        control_rec.location_length[i].length   = -1;
                        corrected = TRUE;
                        }
                    else
                        printf("Permission denied.\n");
                    }
                }
            }

        if (error_flag && fixit && corrected)
            {
            lseek(handle, ctl_file_position, 0);
            write(handle, &control_rec, sizeof(control_rec));
            }

        if (control_rec.next_ctl != 0l)
            {
            lseek(handle, control_rec.next_ctl, 0);
            goto process_control;
            }

        _close(handle);
        }

void    main(int argc, char *argv[])
        {
        oldint24 = getvect(0x24);
        setvect(0x24, int24);

        if (argc < 2)
            {
            printf("USAGE: DIETCHK <filespec>\n");
            return;
            }

        if (argc == 3)
            if (stricmp(argv[2], "/f") == 0)
                fixit = TRUE;

        fnsplit(argv[1], drive, path, name, ext);
        if ( (flag = findfirst(argv[1], &fblock, 0)) != 0 )
            {
            printf("File(s) not found.\n");
            return;
            }

        while (flag == 0)
            {
            check_file();
            flag = findnext(&fblock);
            }

        setvect(0x24, oldint24);

        if (error_flag)
            {
            if (!fixit)
                printf("\nErrors found; corrections not written to disk.\n");
            else
                printf("\nErrors found; file(s) corrected (truncated).\n");
            }
        else
            printf("\nNo errors found.\n");
        }


