
#include <stdio.h>
#include <dos.h>

unsigned int diet_cs = 0;
int far *diet_flag_ptr;

void    main(int argc, char *argv[])
        {
        _AX = 0x3341;
        geninterrupt(0x21);
        if (_DX == 0x1234)
            diet_cs = _CX;

        if (diet_cs == 0)
            printf("Diet Disk not loaded.\n");
        else
            {
            diet_flag_ptr = MK_FP(diet_cs, 0x0103);
            *diet_flag_ptr = 2;
            printf("Diet Disk is now disabled.\n");
            }
        }


