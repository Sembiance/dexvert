section .text
extern  _MessageBoxA@16
%if     __NASM_VERSION_ID__ >= 0x02030000
safeseh handler         ; register handler as "safe handler"
%endif

handler:
        push    dword 1 ; MB_OKCANCEL
        push    dword caption
        push    dword text
        push    dword 0
        call    _MessageBoxA@16
        sub     eax,1   ; incidentally suits as return value
                        ; for exception handler
        ret

global  _main
_main:  push    dword handler
        push    dword [fs:0]
        mov     dword [fs:0], esp
        xor     eax,eax
        mov     eax, dword[eax]   ; cause exception
        pop     dword [fs:0]      ; disengage exception handler
        add     esp, 4
        ret

avx2:   vzeroupper
        push      rbx
        mov       rbx,   rsp
        sub       rsp,   0h20
        vmovdqa   ymm0,  [rcx]
        vpaddb    ymm0,  [rdx]
        leave
        ret

text:   db      'OK to rethrow, CANCEL to generate core dump',0
caption:db      'SEGV',0

section .drectve info
        db      '/defaultlib:user32.lib /defaultlib:msvcrt.lib '
