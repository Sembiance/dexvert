�>SPUTST v1.11 Smooth Talker Utility - (C) 1990 VersaWare / Adrienne Cousins
$                                                                                        file.VMF ST   An error has occurred!$
Error in IOCTL request to device ST$
Error in WRITE request to device ST$
Error in CLOSE request to device ST$��
�J�ܱ����� �!2�� �6�� ��<,t�< t
<t< u���� s��L� L�!�6Q�׉6QN<?u��2���,��!��"��3ɿX�< t<,t< t<t<ar<zw$ߪ����N�6Q3���W�>P u�P����m s���� �� s����� �k��< r0� ���H r&�T r!�F r����4 r�Z r�h r�- � s	��� � ø H���!�Sø I�S�!ô=�!��ô>���!��?��� ��S�ں  �!�UøD���W� �X�!�� D���!�D��� �� �!�@���U�S�ں  �!ô	�!�Voice Master Mode Commands:
        EVM     enable Voice Master Mode (digitized data)
        RDH     read VMF file header (supress playback)
        PLY     playback data file in buffer
        SPE     set playback speed 0-255
        VOL     set playback volume 1-8
        CKE     use 8253 timer for playback speed
        CKD     use software timing for playback speed
        DAC     enable alternate port address 0-65535 (def 408+409)
        WRA     set repeat playback 1-255 0=key
        USR     use alternate user address 100h-1FFh
Press any key to continue...$
Smooth Talker Mode Commands:
        SV2     enable Smooth Talker Mode (SPEECHV2)
        SV3     enable Smooth Talker Mode (SPEECHV3)
        ENG     input will be English strings
        PHO     input will be phonetic strings
        XEP     convert next string from English to Phonetics
        TTE     enable echo of string data to screen
        TTD     disable echo of string data to screen
        CRE     enable carriage returns as string terminator
        CRD     disable carriage returns as string terminator
        FLU     flush the 255 byte string buffer
        TON     set voice tone 0=low 1=high
        SPE     set speed of playback 0-9
        PIT     set pitch of playback 0-9
        VOL     set volume of playback 0-9
Use "COPY <filename> ST" for text files in Smooth Talker Mode
Use "COPY <filename>/B ST" for digitized files in Voice Master Mode
$                                                                                                                                                                                                                                                                 