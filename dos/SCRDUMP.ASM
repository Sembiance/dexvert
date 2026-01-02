; SCRDUMP.COM - dump current 80x25 text screen to SCREEN.TXT
; NASM: nasm -f bin SCRDUMP.ASM -o SCRDUMP.COM

org 100h

start:
    ; Create/truncate SCREEN.TXT
    mov  ah, 3Ch          ; DOS create file
    xor  cx, cx           ; normal attributes
    mov  dx, filename
    int  21h
    jc   done
    mov  [handle], ax

    ; Get current video mode + active page
    mov  ah, 0Fh
    int  10h              ; BH = active page, AL = mode

    ; Compute page offset in bytes: page * 4096 (0x1000)
    ; (In 80x25 text modes, DOS/VGA pages are typically 4KB apart)
    mov  bl, bh
    xor  bh, bh
    mov  ax, bx
    shl  ax, 12           ; ax = page * 4096
    mov  [pageofs], ax

    ; Point ES to color text video memory
    mov  ax, 0B800h
    mov  es, ax

    ; Build output buffer: 25 lines of 80 chars + CRLF
    xor  si, si
    mov  di, buffer

    mov  cx, 25
row_loop:
    push cx
    mov  cx, 80
col_loop:
    ; video offset = pageofs + (row/col offset)
    mov  bx, [pageofs]
    mov  al, es:[bx+si]   ; character byte
    mov  [di], al
    inc  di
    add  si, 2            ; skip attribute byte
    loop col_loop

    mov  byte [di], 13    ; CR
    inc  di
    mov  byte [di], 10    ; LF
    inc  di

    pop  cx
    loop row_loop

    ; Write buffer to file
    mov  bx, [handle]
    mov  ah, 40h
    mov  dx, buffer
    mov  cx, buffer_end - buffer
    int  21h

    ; Close file
    mov  ah, 3Eh
    int  21h

done:
    ret

filename db "SCREEN.TXT",0
handle   dw 0
pageofs  dw 0

buffer:
    ; 25*(80+2)=2050 bytes
    times 2050 db 0
buffer_end:
