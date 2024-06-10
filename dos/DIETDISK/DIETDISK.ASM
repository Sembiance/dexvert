
;-----------------------------------------------------------------;
;                                                                 ;
;       DietDisk   Version 1.0                                    ;
;                                                                 ;
;       Copyright (c) 1990 Barry Nance                            ;
;       Released to the Public Domain                             ;
;                                                                 ;
;       Distributed from BIX, the BYTE Magazine Information       ;
;       Exchange                                                  ;
;                                                                 ;
;-----------------------------------------------------------------;

CallDOS         Macro   _func
                Mov     AH, _func
                PushF
                CLI
                Call    CS:OldInt21
                EndM

;-----------------------------------------------------------------;
;       Equates                                                   ;
;-----------------------------------------------------------------;

StdOut          =       0001            ;file handle for StdOut
MaxName         =       80              ;max size of a filename
MaxHandles      =       10              ;max number of file handles we do
MaxBuf          =       2048            ;buffer size
NumPtrs         =       250             ;number of ptrs on a ptr rec
MaxTextBuf      =       1024            ;text buffer size

;       equates for DOS operations

DiskReset       =       0Dh
FCBOpenOp       =       0Fh
FCBCloseOp      =       10h
FCBSeqReadOp    =       14h
FCBSeqWriteOp   =       15h
FCBCreateOp     =       16h
FCBRandReadOp   =       21h
FCBRandWriteOp  =       22h
FCBFileSizeOp   =       23h
FCBRelRecOp     =       24h
FCBBlockReadOp  =       27h
FCBBlockWriteOp =       28h
CurrentDiskOp   =       19h
SetDTAOp        =       1Ah
GetDTAOp        =       2Fh
GetVerOp        =       30h

SetVectorOp     =       25h
GetVectorOp     =       35h
CreateOp        =       3Ch
OpenOp          =       3Dh
CloseOp         =       3Eh
ReadOp          =       3Fh
WriteOp         =       40h
DeleteOp        =       41h
SeekOp          =       42h
IOCTL           =       44h
DupeHandOp      =       45h
ForceDupeOp     =       46h
GetCurrDir      =       47h
ExecPgmOp       =       4Bh
CreateNewOp     =       5Bh
LockOp          =       5Ch
CommitOp        =       68h
Term00Op        =       00h
Term31Op        =       31h
Term4COp        =       4Ch
FDateTimeOp     =       57h


;       equates for Lempel/Ziv/Welch compression/decompression

clear           =       256             ;Clear code
eof             =       257             ;End of file marker
first_free      =       258             ;First free code
maxmax          =       1024            ;Max code + 1
K512            =       512
K256            =       256
K10             =       10
K9              =       9

;-----------------------------------------------------------------;
;       Physical beginning of program                             ;
;-----------------------------------------------------------------;

PSP             Segment
                Assume  CS:PSP, DS:PSP, ES:PSP
                Org     100h

Program:        Jmp     Start

;-----------------------------------------------------------------;
;       Data area                                                 ;
;-----------------------------------------------------------------;

AskFlag         DW      0
Banner          DB      "Diet Disk V1.0"

DietDir         DB      "Diet.Dir"
                DB      0
LDietDir        =       $ - DietDir

DietPath        DB      MaxName dup(0)
DietDirHandle   DW      ?

DeCompPID       DW      0
DeCompHandle    DW      0
DeCompFilePos   DD      0
DeCompBlock     DW      0FFFFh          ; force it to be read 1st time
DeCompDirty     DW      0

OldPID          DW      ?
CurrHandle      DW      ?
CurrFilePos     DD      ?
CurrBlock       DW      ?
BlockPos        DW      ?

OldInt21        Label   DWord
OldInt21Ofs     DW      ?
OldInt21Seg     DW      ?

OldInt20        Label   DWord
OldInt20Ofs     DW      ?
OldInt20Seg     DW      ?

OldSP           DW      ?
OldSS           DW      ?
OurSP           DW      ?
OurSS           DW      ?
Junk            DW      ?

OurPID          DW      ?
CtrlHandle      DW      ?
CtrlPID         DW      ?
CtrlDirty       DW      0

PtrsHandle      DW      ?
PtrsPID         DW      ?
PtrsFilePos     DD      0016
PtrsDirty       DW      0
PointersStart   DW      0
PointersEnd     DW      NumPtrs-1

CharPos         DW      ?
TablePtr        DW      0
FCBTablePtr     DW      0

;
; table of file handles for skinny files
;
FileHandleTbl   Label   Word
                DW      MaxHandles dup(0FFFFh)

;
; table of Process ID's for the processes that have skinny files
;
PIDTbl          Label   Word
                DW      MaxHandles dup(0FFFFh)

;
; table of current file positions (virtual, not actual) for our files
;

FilePosTbl      Label   DWord
                DD      MaxHandles dup(0)


DupeTable       Label   Word
                DW      MaxHandles*2 dup(0FFFFh)

;
; a table of remembered file names from FCB's created/opened
;

FCBTable        Label   Byte
                DB      MaxHandles * 12 dup(" ")
                DB      0, 0

;
; some buffers (filenames, etc.)
;

NameBuffer      DB      MaxName+2 Dup(0)
CreateName      DB      MaxName+2 Dup(0)
ScreenSave      DB      160       Dup(0)

fbufbytes       DW      0
fbufndx         DW      MaxTextBuf

;
; some other data
;

AskMessage1     Label   Byte
                DB      "Should "
AMLen1          =       $-AskMessage1

AskMessage2     Label   Byte
                DB      " be decompressed? (Y/N)    "
AMLen2          =       $-AskMessage2

ReadErrorMessage Label  Byte
 DB "           Damaged file (disk data may be lost).  Press ды to continue.     "
LReadError      =       $-ReadErrorMessage

WriteErrorMessage Label Byte
 DB " Disk full, or damaged file (disk data may be lost).  Press ды to continue. "
LWriteError     =       $-WriteErrorMessage

TooManyError    Label   Byte
 DB " Too many compressed files open at once (limit 10).  Press ды to continue.  "
LTooManyError   =       $-TooManyError

FileCount       DW      0
AnswerPos       DW      0
CPosSave        DW      0
CTypSave        DW      0

FCBPtr          Label   DWord
FCBOfs          DW      ?
FCBSeg          DW      ?

;
; ApplBufferPtr stores the DX:DS buffer pointer for certain DOS operations
;

ApplBufferPtr   Label   DWord
CreatePtr       Label   DWord
R_DX            DW      ?               ; register contents at entry to DOS
R_DS            DW      ?
R_CX            DW      ?
R_AL            DB      ?
R_AX            DW      ?
R_SI            DW      ?
R_DI            DW      ?

;
; some more data
;

DietEOF         DW      ?
CreateLength    DW      ?
DirLength       DW      ?

OurDTA          Label   DWord
OurDTAOfs       DW      ?
OurDTASeg       DW      ?
OldDTA          Label   DWord
OldDTAOfs       DW      ?
OldDTASeg       DW      ?

EndOfBlock      DW      ?
BytesMoved      DW      ?
RD_ONLY         DB      ?
RD_WR           DB      ?
CompressLength  DW      ?
FirstEmpty      DB      ?

NumBlocks       DW      ?
AdvancePtr      DW      ?
TotalLength     DD      ?

PointerBlock    DW      0
LinkLength      DW      ?
LinkLocation    DD      ?

CurrLen         DW      ?
CurrPtr         DD      ?
LenToWrite      DW      ?
NextPtr         DD      ?
PrevPtr         DD      ?
NextLen         DW      ?
PtrRecSegment   DW      ?
WritePtr        DW      ?

GetCtrlHandle   DW      ?
GetCtrlPID      DW      ?
GetPtrsHandle   DW      ?
GetPtrsPID      DW      ?
PutCtrlHandle   DW      ?
PutCtrlPID      DW      ?
PutPtrsHandle   DW      ?
PutPtrsPID      DW      ?

CritFlag        DW      0
DOSVersion      DB      ?
DOSVersMin      DB      ?
IOFlag          DW      0

Int24Ptr        Label   DWord
Int24Ofs        DW      ?
Int24Seg        DW      ?

;
; a buffer for reading files to see if they have a footprint
;

FootBuffer      DB      16 dup(?)


;
; a "zero-mask" for the control record
;

Control_ZM      Label   Byte
                DB      "lZdIeT"        ; footprint (6 bytes)
                DD      0               ; current file length (virtual)
                DB      6 dup(0)        ; filler 
Ctrl_ZM_Size    =       $-Control_ZM

;
; I/O and de-compression buffers
;

                Even
CtrlBuffer      Label   Byte
  CtrlFootPrint DB      6 dup(?)
  Ctrl_FileLen  DD      ?       
                DB      6 dup(?) 
CtrlSize        =       $-CtrlBuffer

                Even
Ctrl_Pointers   Label   Byte
  Ctrl_Next     DD      ?
  Ctrl_Prev     DD      ?
                DB      8 dup(?) 
  Loc_Len_Info  DB      NumPtrs*6 dup(?)
PtrsSize        =       $-Ctrl_Pointers

  EndOfCtrlRec  Label   Byte


                Even
DeCompBuffer    Label   Byte
  ILinkPtr      DD      ?
  ILinkLen      DW      ?
                DB      MaxBuf+512  dup(?)

                Even
IOBuffer        Label   Byte
  OLinkPtr      DD      ?
  OLinkLen      DW      ?
                DB      MaxBuf+512  dup(?)


;
;Hash table
;

                Even
Hash            Label   Byte

Next            DW      ?               ; Next entry along chain
                DW      maxmax dup(?)

Char            DB      ?               ; Suffix char
                DB      maxmax dup(?)

First           DW      ?               ; First entry with this value
                DW      maxmax dup(?)


;
; other compression-related items
;

Prefix_Code     DW      ?
Free_Code       DW      ?
Max_Code        DW      ?
NBits           DW      ?
K               DB      ?
Bit_Offset      DW      ?
Input_Offset    DW      0
Input_Size      DW      0
Cur_Code        DW      ?
Old_Code        DW      ?
In_Code         DW      ?
Stack_Count     DW      0
Fin_Char        DB      ?
Masks           DW      1ffh, 3ffh, 7ffh, 0fffh
Output_Offset   DW      0


;-----------------------------------------------------------------;
;       INT 21 interception                                       ;
;-----------------------------------------------------------------;
DOS_Handler     Proc    Far

ISR_21:
                PushF
                STI

                Mov     CS:IOFlag, 0

CaseFunc00:
                Cmp     AH, Term00Op
                JNE     CaseFunc31
                Jmp     DoTerm
CaseFunc31:
                Cmp     AH, Term31Op
                JNE     CaseFunc4C
                Jmp     DoTerm
CaseFunc4C:
                Cmp     AH, Term4COp
                JNE     CaseCreate
                Jmp     DoTerm
CaseCreate:
                Cmp     AH, CreateOp
                JNE     CaseOpen
                Jmp     DoCreate
CaseOpen:
                Cmp     AH, OpenOp
                JNE     CaseClose
                Jmp     DoOpen
CaseClose:
                Cmp     AH, CloseOp
                JNE     CaseRead
                Jmp     DoClose
CaseRead:
                Cmp     AH, ReadOp
                JNE     CaseWrite
                Jmp     DoRead
CaseWrite:
                Cmp     AH, WriteOp
                JNE     CaseSeek
                Jmp     DoWrite
CaseSeek:
                Cmp     AH, SeekOp
                JNE     CaseDupe
                Jmp     DoSeek
CaseDupe:
                Cmp     AH, DupeHandOp
                JNE     CaseForceDupe
                Jmp     DoDupe
CaseForceDupe:
                Cmp     AH, ForceDupeOp
                JNE     CaseLock
                Jmp     DoForceDupe
CaseLock:
                Cmp     AH, LockOp
                JNE     CaseCreateNew
                Jmp     DoLockUnlock
CaseCreateNew:
                Cmp     AH, CreateNewOp
                JNE     CaseFCBOpen
                Jmp     DoCreateNew
CaseFCBOpen:
                Cmp     AH, FCBOpenOp
                JNE     CaseFCBClose
                Jmp     DoFCBOpen
CaseFCBClose:
                Cmp     AH, FCBCloseOp
                JNE     CaseFCBSeqRead
                Jmp     DoFCBClose
CaseFCBSeqRead:
                Cmp     AH, FCBSeqReadOp
                JNE     CaseFCBSeqWrite
                Jmp     DoFCBSeqRead
CaseFCBSeqWrite:
                Cmp     AH, FCBSeqWriteOp
                JNE     CaseFCBCreate
                Jmp     DoFCBSeqWrite
CaseFCBCreate:
                Cmp     AH, FCBCreateOp
                JNE     CaseFCBRandRead
                Jmp     DoFCBCreate
CaseFCBRandRead:
                Cmp     AH, FCBRandReadOp
                JNE     CaseFCBRandWrite
                Jmp     DoFCBRandRead
CaseFCBRandWrite:
                Cmp     AH, FCBRandWriteOp
                JNE     CaseFCBFileSize
                Jmp     DoFCBRandWrite
CaseFCBFileSize:
                Cmp     AH, FCBFileSizeOp
                JNE     CaseFCBBlockRead
                Jmp     DoFCBFileSize
CaseFCBBlockRead:
                Cmp     AH, FCBBlockReadOp
                JNE     CaseFCBBlockWrite
                Jmp     DoFCBBlockRead
CaseFCBBlockWrite:
                Cmp     AH, FCBBlockWriteOp
                JNE     CaseCtlBrkCheck
                Jmp     DoFCBBlockWrite
CaseCtlBrkCheck:
                Cmp     AX, 3341h
                JNE     DefaultDOS
                Jmp     DoInstalledResponse

DefaultDOS:
                PopF
                Jmp     CS:OldInt21     ; let DOS handle it normally


;-----------------------------------------------------------------;
;       AX=3341h, Int 21h asks if we are loaded.  Answer yes.     ;
;-----------------------------------------------------------------;

DoInstalledResponse:
                Mov     DX, 1234h
                Mov     CX, CS
                Mov     CS:IOFlag, 0
                Jmp     ExitDOS



;-----------------------------------------------------------------;
;       Handle Program Terminate Functions                        ;
;-----------------------------------------------------------------;
DoTerm:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Call    CloseRemaining

                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS




;-----------------------------------------------------------------;
;       Handle Create-File Function Call                          ;
;-----------------------------------------------------------------;


DoCreate:
                CallDOS CreateOp
                JNC     DoCreate_1
                Jmp     BadDOS          ; if not created, don't process

DoCreate_1:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DS, DS     ; save ptr to AsciiZ name
                Mov     CS:R_DX, DX

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Mov     CurrHandle, AX

                Call    GetOldPID
                Call    SearchTable
                JC      DoCreate_5
                Call    ForgetThisFile

DoCreate_5:
                Call    SearchDietDir   ; look in the Diet.Dir file
                JC      DoCreate_9      ; if not in Diet.Dir

                Call    WriteInitControl ; initialize skinny file
                Call    RememberThisFile

DoCreate_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     ExitDOS


;-----------------------------------------------------------------;
;       Handle Open-File Function Call                            ;
;-----------------------------------------------------------------;

DoOpen:
                CallDOS OpenOp
                JNC     DoOpen_1
                Jmp     BadDOS          ; if bad open, we can't do anything

DoOpen_1:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DS, DS     ; save ptr to AsciiZ name
                Mov     CS:R_DX, DX

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Mov     CurrHandle, AX
                Call    GetOldPID       ; which process is opening a file?

                Call    SearchTable
                JC      DoOpen_5

                Call    ForgetThisFile

DoOpen_5:
                Cmp     AskFlag, 2
                JNE     DoOpen_5A
                Jmp     DoOpen_9

DoOpen_5A:      Call    ReadFootPrint
                JNC     DoOpen_5B
                Jmp     DoOpen_9

DoOpen_5B:      Cmp     AskFlag, 1
                JNE     DoOpen_7

                Call    SaveLine25
                JC      DoOpen_7

                Mov     DX, 1800h
                Mov     AnswerPos, 0
                Mov     DI, Offset AskMessage1
                Mov     CX, AMLen1
                Add     AnswerPos, CX
                Call    AttrCharOut

                Push    DX
                Call    Parse_DS_DX_Name
                Pop     DX

                Mov     DI, Offset CreateName
                Mov     CX, CreateLength
                Add     AnswerPos, CX
                Call    AttrCharOut
                Mov     DI, Offset AskMessage2
                Mov     CX, AMLen2
                Add     AnswerPos, CX
                Call    AttrCharOut

GetAnswer:      
                Mov     AH, 2
                Mov     BH, 0
                Mov     DX, 1800h
                Add     DX, AnswerPos
                Dec     DX
                Dec     DX
                Int     10h

                Mov     AH, 0
                Int     16h
                Cmp     AL, 'Y'
                JE      AnswerIsYes
                Cmp     AL, 'y'
                JE      AnswerIsYes
                Cmp     AL, 'N'
                JE      AnswerIsNo
                Cmp     AL, 'n'
                JE      AnswerIsNo
                Jmp     GetAnswer

AnswerIsNo:
                Call    RestLine25
                Jmp     DoOpen_9

AnswerIsYes:
                Call    RestLine25
DoOpen_7:
                Call    RememberThisFile ; save file handle, etc. in table

                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     GetPtrsHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Mov     GetPtrsPID, AX
                Call    GetControlRec
                Mov     PointerBlock, 0
                Call    GetPointerRec

DoOpen_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; back to the application
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     ExitDOS


;-----------------------------------------------------------------;
;       Handle Close-File Function Call                           ;
;-----------------------------------------------------------------;

DoClose:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Mov     CurrHandle, BX
                Call    GetOldPID       ; process that's closing a file
                Call    SearchTable     ; is it one of ours?
                JC      DoClose_9       ; no

                Mov     BX, CurrHandle
                Cmp     BX, DeCompHandle
                JNE     DoClose_8

                Mov     AL, 0
                CallDOS FDateTimeOp
                Push    CX
                Push    DX
                Call    PutBlock
                Call    WritePointerRec
                Call    WriteTheCtrlRec
                Pop     DX
                Pop     CX
                Mov     BX, CurrHandle
                Mov     AL, 1
                CallDOS FDateTimeOp

DoClose_8:      
                Call    ForgetThisFile

DoClose_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; back to the application
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
 
                Jmp     DefaultDOS


;-----------------------------------------------------------------;
;       Handle Read-File Function Call                            ;
;-----------------------------------------------------------------;

DoRead:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:R_DS, DS
                Mov     CS:R_DX, DX
                Mov     CS:R_CX, CX

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;
                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoRead_1        ; it's a skinny file

                Jmp     DoRead_9        ; not one of ours (let DOS do it)

DoRead_1:
                Call    Get_CX_Bytes_To_DSDX
                Call    AlignDupedFiles

DoRead_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; read request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Mov     AX, CS:BytesMoved
                Jmp     ExitDOS


;
; file is not skinny....let DOS handle it.
;

DoRead_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS


;-----------------------------------------------------------------;
;       Handle Write-File Function Call                           ;
;-----------------------------------------------------------------;

DoWrite:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:R_DS, DS
                Mov     CS:R_DX, DX
                Mov     CS:R_CX, CX

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;
                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoWrite_1       ; it's a skinny file

                Jmp     DoWrite_9       ; not one of ours (let DOS do it)

DoWrite_1:
                Call    Put_CX_Bytes_From_DSDX

                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; write request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Mov     AX, CS:BytesMoved
                Jmp     ExitDOS


;
; file is not skinny....let DOS handle it.
;

DoWrite_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS

;-----------------------------------------------------------------;
;       Handle Seek-File Function Call                            ;
;-----------------------------------------------------------------;

DoSeek:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:R_DX, DX
                Mov     CS:R_CX, CX
                Mov     CS:R_AL, AL

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;

                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoSeek_0        ; it's a skinny file

                Jmp     DoSeek_9        ; not one of ours (let DOS do it)

DoSeek_0:
                Mov     BX, TablePtr
                Shl     BX, 1
                Mov     CX, R_CX
                Mov     DX, R_DX

                Cmp     R_AL, 0
                JNE     DoSeek_1

;
; seek from *beginning* of file
;
                Mov     Word Ptr FilePosTbl [BX], DX
                Mov     Word Ptr FilePosTbl [BX+2], CX

                Jmp     DoSeek_8

DoSeek_1:
                Cmp     R_AL, 1
                JNE     DoSeek_2

;
; seek from *current* position
;
                Add     DX, Word Ptr FilePosTbl [BX]
                Adc     CX, Word Ptr FilePosTbl [BX+2]
                Mov     Word Ptr FilePosTbl [BX], DX
                Mov     Word Ptr FilePosTbl [BX+2], CX

                Jmp     DoSeek_8


DoSeek_2:
;
; seek from *end* of file
;
                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Call    GetControlRec

                Add     DX, Word Ptr Ctrl_FileLen
                Adc     CX, Word Ptr Ctrl_FileLen+2
                Mov     Word Ptr FilePosTbl [BX], DX
                Mov     Word Ptr FilePosTbl [BX+2], CX

DoSeek_8:       
                Mov     R_CX, CX
                Mov     R_DX, DX

                Call    AlignDupedFiles

                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; seek request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Mov     DX, Word Ptr CS:R_CX
                Mov     AX, Word Ptr CS:R_DX

                Jmp     ExitDOS


;
; file is not skinny....let DOS handle it.
;

DoSeek_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS



;-----------------------------------------------------------------;
;       Handle Dupe-Handle Function Call                          ;
;-----------------------------------------------------------------;

DoDupe:         CallDOS DupeHandOp
                JNC     DoDupe_0
                Jmp     BadDOS

DoDupe_0:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_AX, AX

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoDupe_1        ; it's a skinny file

                Jmp     DoDupe_8        ; not one of ours (let DOS do it)

DoDupe_1:
                Push    TablePtr
                Mov     AX, R_AX
                Mov     CurrHandle, AX
                Call    RememberThisFile

                Call    SearchTable

                Mov     DI, TablePtr
                Pop     TablePtr
                Mov     SI, TablePtr
                Mov     DupeTable [DI], SI
                Mov     DupeTable [SI], DI

                Call    AlignDupedFiles

DoDupe_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     ExitDOS



;-----------------------------------------------------------------;
;       Handle Force-Dupe-Handle Function Call                    ;
;-----------------------------------------------------------------;

DoForceDupe:    CallDOS ForceDupeOp
                JNC     DoForce_0
                Jmp     BadDOS

DoForce_0:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_CX, CX

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoForce_1       ; it's a skinny file

                Jmp     DoForce_8       ; not one of ours (let DOS do it)

DoForce_1:
                Push    TablePtr
                Mov     CX, R_CX
                Mov     CurrHandle, CX
                Call    RememberThisFile

                Mov     DI, TablePtr
                Pop     TablePtr
                Mov     SI, TablePtr
                Mov     DupeTable [DI], SI
                Mov     DupeTable [SI], DI

                Call    AlignDupedFiles

DoForce_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     ExitDOS




;-----------------------------------------------------------------;
;       Handle Lock/Unlock Function Call                          ;
;-----------------------------------------------------------------;

DoLockUnlock:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_AL, AL
                Mov     CS:R_CX, CX
                Mov     CS:R_DX, DX
                Mov     CS:R_SI, SI
                Mov     CS:R_DI, DI

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Mov     CurrHandle, BX
                Call    GetOldPID
                Call    SearchTable
                JNC     DoLock_0        ; it's a skinny file

                Jmp     DoLock_9        ; not one of ours (let DOS do it)

DoLock_0:
                Mov     BX, CurrHandle
                Mov     CX, 0
                Mov     DX, CX
                Mov     SI, 0FFFFh
                Mov     DI, SI
                Mov     AL, R_AL
                CallDOS LockOp
                JNC     LockOk

                Mov     R_AX, AX
                CLI
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     BadDOS


LockOk:         CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     ExitDOS



DoLock_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS




;-----------------------------------------------------------------;
;       Handle Create-New Function Call                           ;
;-----------------------------------------------------------------;

DoCreateNew:
                CallDOS CreateNewOp
                JNC     DoCreateNew_0
                Jmp     BadDOS

DoCreateNew_0:
                Jmp     DoCreate_1





;-----------------------------------------------------------------;
;       Handle FCB Open Function Call                             ;
;-----------------------------------------------------------------;

DoFCBOpen:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Call    GetOldPID

                Call    SearchFCBTable
                JC      FCBOpen_0

                Mov     SI, TablePtr
                Mov     BX, FileHandleTbl [SI]
                Mov     CurrHandle, BX

                Jmp     FCBOpen_7

; Parse FCB name into NameBuffer and then do a regular handle-open.

FCBOpen_0:
                Call    ParseFCBName

                Mov     DX, Offset NameBuffer
                Mov     AL, 02
                CallDOS OpenOp
                JNC     FCBOpenOk
                Mov     DX, Offset NameBuffer
                Mov     AL, 00
                CallDOS OpenOp
                JNC     FCBOpenOk

                Jmp     FCBOpen_9

FCBOpenOk:
                Mov     CurrHandle, AX
                Call    GetOldPID       ; which process is opening a file?
                Call    SearchTable     ; get a TablePtr value

FCBOpen_5:
                Cmp     AskFlag, 2
                JNE     FCBOpen_5A
                
                Mov     BX, CurrHandle
                CallDOS CloseOp
                Jmp     FCBOpen_9

FCBOpen_5A:     Call    ReadFootPrint   ; look for our footprint
                JNC     FCBOpen_5B

                Mov     BX, CurrHandle
                CallDOS CloseOp
                Jmp     FCBOpen_9       ; not there...it's not skinny

FCBOpen_5B:
                Cmp     AskFlag, 1
                JNE     FCBOpen_7

                Call    SaveLine25
                JC      FCBOpen_7

                Mov     DX, 1800h
                Mov     AnswerPos, 0
                Mov     DI, Offset AskMessage1
                Mov     CX, AMLen1
                Add     AnswerPos, CX
                Call    AttrCharOut

                Mov     DI, Offset NameBuffer
                Mov     CX, CreateLength
                Add     AnswerPos, CX
                Call    AttrCharOut
                Mov     DI, Offset AskMessage2
                Mov     CX, AMLen2
                Add     AnswerPos, CX
                Call    AttrCharOut

FCBGetAnswer:      
                Mov     AH, 2
                Mov     BH, 0
                Mov     DX, 1800h
                Add     DX, AnswerPos
                Dec     DX
                Dec     DX
                Int     10h

                Mov     AH, 0
                Int     16h
                Cmp     AL, 'Y'
                JE      FCBAnswerIsYes
                Cmp     AL, 'y'
                JE      FCBAnswerIsYes
                Cmp     AL, 'N'
                JE      FCBAnswerIsNo
                Cmp     AL, 'n'
                JE      FCBAnswerIsNo
                Jmp     FCBGetAnswer

FCBAnswerIsNo:
                Call    RestLine25
                Mov     BX, CurrHandle
                CallDOS CloseOp
                Jmp     FCBOpen_9

FCBAnswerIsYes:
                Call    RestLine25
FCBOpen_7:
                Call    RememberThisFile ; save file handle, etc. in table

                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     GetPtrsHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Mov     GetPtrsPID, AX
                Call    GetControlRec
                Mov     PointerBlock, 0
                Call    GetPointerRec

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBOpen_7A
                Add     DI, 7
FCBOpen_7A:
                Mov     BP, DI
                Cmp     Byte Ptr ES:[DI], 0
                JNE     FCBOpen_7B

                CallDOS CurrentDiskOp
                Inc     AL
                Mov     Byte Ptr ES:[DI], AL

FCBOpen_7B:
                Mov     Word Ptr ES:[DI+12], 0
                Mov     Word Ptr ES:[DI+14], 80h
                Mov     BX, CurrHandle
                Mov     AL, 0
                CallDOS FDateTimeOp
                Mov     Word Ptr ES:[DI+20], DX

                Mov     AX, Word Ptr Ctrl_FileLen
                Mov     Word Ptr ES:[DI+16], AX
                Mov     AX, Word Ptr Ctrl_FileLen+2
                Mov     Word Ptr ES:[DI+18], AX

                Push    DS
                Pop     ES

                Mov     AX, 12
                Mul     TablePtr
                Mov     DI, Offset FCBTable
                Add     DI, AX
                Mov     CX, 6
                Push    DS
                Mov     DS, FCBSeg
                Mov     SI, BP
        Rep     MovSW
                Pop     DS

FCBOpen_8:
                Mov     R_AX, 0F00h
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



FCBOpen_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS




;-----------------------------------------------------------------;
;       Handle FCB Close Function Call                            ;
;-----------------------------------------------------------------;

DoFCBClose:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Call    SearchFCBTable
                JNC     FCBClose_ThisOne

                Jmp     DoFCBClose_9    ; not one of ours (let DOS do it)

FCBClose_ThisOne:
                Mov     SI, TablePtr
                Mov     BX, FileHandleTbl [SI]
                Mov     CurrHandle, BX
                Call    GetOldPID       ; process that's closing a file

                Mov     BX, CurrHandle
                Cmp     BX, DeCompHandle
                JNE     FCBClose_7

                Mov     AL, 0
                CallDOS FDateTimeOp
                Push    CX
                Push    DX
                Call    PutBlock
                Call    WritePointerRec
                Call    WriteTheCtrlRec
                Pop     DX
                Pop     CX
                Mov     BX, CurrHandle
                Mov     AL, 1
                CallDOS FDateTimeOp

FCBClose_7:
                Call    ForgetThisFile
                Mov     BX, CurrHandle
                CallDOS CloseOp

                Push    DS
                Pop     ES
                Mov     DI, FCBTablePtr
                Mov     CX, 6
                Mov     AX, 2020h
        Rep     StoSW

DoFCBClose_8:
                Mov     R_AX, 1000h
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBClose_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS




;-----------------------------------------------------------------;
;       Handle FCB Seq Read Function Call                         ;
;-----------------------------------------------------------------;

DoFCBSeqRead:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS


                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Call    SearchFCBTable
                JNC     DoFCBSeqRead_0  ; it's a skinny file

                Jmp     DoFCBSeqRead_9  ; not one of ours (let DOS do it)

DoFCBSeqRead_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBSeqReadNotExt
                Add     DI, 7
FCBSeqReadNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     R_CX, CX

                Xor     AX, AX
                Mov     AL, Byte Ptr ES:[DI+32]
                Mov     BP, AX
                Mov     AX, 128
                Mul     Word Ptr ES:[DI+12]
                Add     AX, BP
                Adc     DX, 0

                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2A
                MUL     BX
LMul2A:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3A
                MUL     SI
                ADD     CX,AX
LMul3A:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Get_CX_Bytes_To_DSDX

                Mov     R_AX, 1400h
                Cmp     R_CX, 0
                JE      FCBSeqRead_5

                Cmp     BytesMoved, 0
                JA      FCBSeqReadSomeBytes

                Mov     R_AX, 1401h
                Jmp     FCBSeqRead_5

FCBSeqReadSomeBytes:
                Mov     AX, BytesMoved
                Cmp     AX, R_CX
                JE      FCBSeqRead_5

                Mov     R_AX, 1403h

FCBSeqRead_5:
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBSeqReadNotExt2
                Add     DI, 7

FCBSeqReadNotExt2:
                Inc     Byte Ptr ES:[DI+32]
                Cmp     Byte Ptr ES:[DI+32], 80h
                JB      DoFCBSeqRead_8

                Mov     Byte Ptr ES:[DI+32], 0
                Inc     Word Ptr ES:[DI+12]

DoFCBSeqRead_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBSeqRead_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB Seq Write Function Call                        ;
;-----------------------------------------------------------------;

DoFCBSeqWrite:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?

                Call    SearchFCBTable
                JNC     DoFCBSeqWrite_0  ; it's a skinny file

                Jmp     DoFCBSeqWrite_9  ; not one of ours (let DOS do it)

DoFCBSeqWrite_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBSeqWriteNotExt
                Add     DI, 7
FCBSeqWriteNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     R_CX, CX

                Xor     AX, AX
                Mov     AL, Byte Ptr ES:[DI+32]
                Mov     BP, AX
                Mov     AX, 128
                Mul     Word Ptr ES:[DI+12]
                Add     AX, BP
                Adc     DX, 0

                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2B
                MUL     BX
LMul2B:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3B
                MUL     SI
                ADD     CX,AX
LMul3B:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Put_CX_Bytes_From_DSDX

                Mov     R_AX, 1500h

                Mov     AX, BytesMoved
                Cmp     AX, R_CX
                JE      FCBSeqWrite_5

                Mov     R_AX, 1501h

FCBSeqWrite_5:
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBSeqWriteNotExt2
                Add     DI, 7

FCBSeqWriteNotExt2:
                Inc     Byte Ptr ES:[DI+32]
                Cmp     Byte Ptr ES:[DI+32], 80h
                JB      FCBSeqWriteSameBlock

                Mov     Byte Ptr ES:[DI+32], 0
                Inc     Word Ptr ES:[DI+12]

FCBSeqWriteSameBlock:
                Mov     AX, Word Ptr Ctrl_FileLen
                Mov     Word Ptr ES:[DI+16], AX
                Mov     AX, Word Ptr Ctrl_FileLen+2
                Mov     Word Ptr ES:[DI+18], AX

DoFCBSeqWrite_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBSeqWrite_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB Create Function Call                           ;
;-----------------------------------------------------------------;

DoFCBCreate:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Call    GetOldPID

                Call    SearchFCBTable
                JC      FCBCreate_0

                Mov     SI, TablePtr
                Mov     BX, FileHandleTbl [SI]
                Mov     CurrHandle, BX
                CallDOS CloseOp
                Call    ParseFCBName
                Mov     DX, Offset NameBuffer
                CallDOS DeleteOp
                Call    ForgetThisFile

                Push    DS
                Pop     ES
                Mov     DI, FCBTablePtr
                Mov     CX, 6
                Mov     AX, 2020h
        Rep     StoSW


; Parse FCB name into FootBuffer and then do a regular handle-create.

FCBCreate_0:
                Call    ParseFCBName
                Mov     CX, CreateLength
                Inc     CX
                Mov     DI, Offset FootBuffer
                Mov     SI, Offset NameBuffer
        Rep     MovSB

                Mov     R_DX, Offset FootBuffer
                Mov     R_DS, DS

                Call    SearchDietDir
                JNC     FCBCreate_1

                Jmp     FCBCreate_9

FCBCreate_1:
                Mov     DX, Offset FootBuffer
                Mov     CX, 0
                CallDOS CreateOp
                JNC     FCBCreateOk

                Jmp     FCBCreate_9

FCBCreateOk:
                Mov     CurrHandle, AX
                Call    SearchTable     ; get a TablePtr value

                Call    WriteInitControl ; initialize skinny file
                Call    RememberThisFile


FCBCreatedAlready:
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBCreate_7A
                Add     DI, 7
FCBCreate_7A:
                Mov     BP, DI
                Cmp     Byte Ptr ES:[DI], 0
                JNE     FCBCreate_7B

                CallDOS CurrentDiskOp
                Inc     AL
                Mov     Byte Ptr ES:[DI], AL

FCBCreate_7B:
                Mov     Word Ptr ES:[DI+12], 0
                Mov     Word Ptr ES:[DI+14], 80h
                Mov     BX, CurrHandle
                Mov     AL, 0
                CallDOS FDateTimeOp
                Mov     Word Ptr ES:[DI+20], DX

                Mov     Word Ptr ES:[DI+16], 0
                Mov     Word Ptr ES:[DI+18], 0

                Push    DS
                Pop     ES

                Mov     AX, 12
                Mul     TablePtr
                Mov     DI, Offset FCBTable
                Add     DI, AX
                Mov     CX, 6
                Push    DS
                Mov     DS, FCBSeg
                Mov     SI, BP
        Rep     MovSW
                Pop     DS

FCBCreate_8:
                Mov     R_AX, 1600h
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



FCBCreate_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB Rand Read Function Call                        ;
;-----------------------------------------------------------------;

DoFCBRandRead:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;

                Call    SearchFCBTable
                JNC     DoFCBRndRead_0  ; it's a skinny file

                Jmp     DoFCBRndRead_9  ; not one of ours (let DOS do it)

DoFCBRndRead_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBRndReadNotExt
                Add     DI, 7
FCBRndReadNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     R_CX, CX

                Mov     AX, Word Ptr ES:[DI+33]
                Cmp     CX, 64
                JB      FCBRndReadRecNLT64

                Xor     DX, DX
                Mov     DL, Byte Ptr ES:[DI+35]
                Jmp     FCBRndReadGotRecN

FCBRndReadRecNLT64:
                Mov     DX, Word Ptr ES:[DI+35]

FCBRndReadGotRecN:
                Push    AX
                Push    DX

                Mov     CX, 128
                DIV     CX
                Mov     Word Ptr ES:[DI+12], AX
                Mov     Byte Ptr ES:[DI+32], DL

                Pop     DX
                Pop     AX
                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2C
                MUL     BX
LMul2C:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3C
                MUL     SI
                ADD     CX,AX
LMul3C:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Get_CX_Bytes_To_DSDX

                Mov     R_AX, 2100h
                Cmp     R_CX, 0
                JE      FCBRndRead_5

                Cmp     BytesMoved, 0
                JA      FCBRndReadSomeBytes

                Mov     R_AX, 2101h
                Jmp     FCBRndRead_5

FCBRndReadSomeBytes:
                Mov     AX, BytesMoved
                Cmp     AX, R_CX
                JE      FCBRndRead_5

                Mov     R_AX, 2103h

FCBRndRead_5:

DoFCBRandRead_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBRndRead_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB Rand Write Function Call                       ;
;-----------------------------------------------------------------;

DoFCBRandWrite:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS

                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;

                Call    SearchFCBTable
                JNC     DoFCBRndWrite_0  ; it's a skinny file

                Jmp     DoFCBRndWrite_9  ; not one of ours (let DOS do it)

DoFCBRndWrite_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBRndWriteNotExt
                Add     DI, 7
FCBRndWriteNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     R_CX, CX

                Mov     AX, Word Ptr ES:[DI+33]
                Cmp     Word Ptr ES:[DI+14], 64
                JB      FCBRndWriteRecNLT64

                Xor     DX, DX
                Mov     DL, Byte Ptr ES:[DI+35]
                Jmp     FCBRndWriteGotRecN

FCBRndWriteRecNLT64:
                Mov     DX, Word Ptr ES:[DI+35]

FCBRndWriteGotRecN:
                Push    AX
                Push    DX

                Mov     CX, 128
                DIV     CX
                Mov     Word Ptr ES:[DI+12], AX
                Mov     Byte Ptr ES:[DI+32], DL

                Pop     DX
                Pop     AX
                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2D
                MUL     BX
LMul2D:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3D
                MUL     SI
                ADD     CX,AX
LMul3D:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Put_CX_Bytes_From_DSDX

                Mov     R_AX, 2200h
                Mov     CX, R_CX
                Cmp     BytesMoved, CX
                JE      DoFCBRandWrite_8

                Mov     R_AX, 2201h

DoFCBRandWrite_8:
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBRandWrite_AdjLen
                Add     DI, 7

FCBRandWrite_AdjLen:
                Mov     AX, Word Ptr Ctrl_FileLen
                Mov     Word Ptr ES:[DI+16], AX
                Mov     AX, Word Ptr Ctrl_FileLen+2
                Mov     Word Ptr ES:[DI+18], AX

DoFCBRandWrite_8A:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBRndWrite_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB File Size Function Call                        ;
;-----------------------------------------------------------------;

DoFCBFileSize:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

DoFCBFileSize_0:
                Mov     R_AX, 0
                Call    ParseFCBName

                Mov     DX, Offset NameBuffer
                Mov     AL, RD_ONLY
                CallDOS OpenOp
                JNC     DoFCBFileSize_1

                Jmp     DoFCBFileSize_9

DoFCBFileSize_1:
                Mov     CurrHandle, AX
                Call    GetOldPID

                Call    ReadFootPrint
                JNC     DoFCBFileSize_3

                Mov     BX, CurrHandle
                CallDOS CloseOp
                Jmp     DoFCBFileSize_9

DoFCBFileSize_3:
                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Call    GetControlRec
                Mov     AX, Word Ptr Ctrl_FileLen
                Mov     DX, Word Ptr Ctrl_FileLen+2

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBFileSizeNotExt
                Add     DI, 7

FCBFileSizeNotExt:
                Mov     BP, 0
                Mov     BX, Word Ptr ES:[DI+14]
                Call    LongDiv

                Mov     Word Ptr ES:[DI+33], AX

                Cmp     Word Ptr ES:[DI+14], 64
                JB      FCBFileSizeLT64
                Mov     Byte Ptr ES:[DI+35], DL
                Jmp     FCBFileSize_7

FCBFileSizeLT64:
                Mov     Word Ptr ES:[DI+35], DX

FCBFileSize_7:
                Mov     BX, CurrHandle
                CallDOS CloseOp

DoFCBFileSize_8:
                Mov     R_AX, 2300h
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX

                Jmp     ExitDOS



DoFCBFileSize_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS


;-----------------------------------------------------------------;
;       Handle FCB Block Read Function Call                       ;
;-----------------------------------------------------------------;

DoFCBBlockRead:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_CX, CX
                Mov     CS:R_DX, DX
                Mov     CS:R_DS, DS
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;

                Call    SearchFCBTable
                JNC     DoFCBBlkRead_0  ; it's a skinny file

                Jmp     DoFCBBlkRead_9  ; not one of ours (let DOS do it)

DoFCBBlkRead_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBBlkReadNotExt
                Add     DI, 7
FCBBlkReadNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     Junk, CX
                Mov     AX, R_CX
                Mul     CX
                Mov     R_CX, AX

                Mov     AX, Word Ptr ES:[DI+33]
                Cmp     Word Ptr ES:[DI+14], 64
                JB      FCBBlkReadRecNLT64

                Xor     DX, DX
                Mov     DL, Byte Ptr ES:[DI+35]
                Jmp     FCBBlkReadGotRecN

FCBBlkReadRecNLT64:
                Mov     DX, Word Ptr ES:[DI+35]

FCBBlkReadGotRecN:
                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2E
                MUL     BX
LMul2E:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3E
                MUL     SI
                ADD     CX,AX
LMul3E:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Get_CX_Bytes_To_DSDX

                Mov     R_AX, 2700h
                Cmp     R_CX, 0
                JE      FCBBlkRead_5

                Cmp     BytesMoved, 0
                JA      FCBBlkReadSomeBytes

                Mov     R_AX, 2701h
                Jmp     FCBBlkRead_5

FCBBlkReadSomeBytes:
                Mov     AX, BytesMoved
                Cmp     AX, R_CX
                JE      FCBBlkRead_5

                Mov     R_AX, 2701h

FCBBlkRead_5:
                Mov     AX, BytesMoved
                Xor     DX, DX
                Div     Junk
                Mov     R_CX, AX
 
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBBlkRead_6
                Add     DI, 7
FCBBlkRead_6:
                Cmp     Word Ptr ES:[DI+14], 64
                JAE     FCBBlkRead_6A
                Add     Word Ptr ES:[DI+33], AX
                Adc     Word Ptr ES:[DI+35], 0
                Jmp     FCBBlkRead_6B

FCBBlkRead_6A:
                Add     Word Ptr ES:[DI+33], AX
                Adc     Byte Ptr ES:[DI+35], 0

FCBBlkRead_6B:
                Mov     CX, AX
                JCXZ    FCBBlkRead_8
FCBBlkRead_7:
                Inc     Byte Ptr ES:[DI+32]
                Cmp     Byte Ptr ES:[DI+32], 128
                JB      FCBBlkRead_7A
 
                Mov     Byte Ptr ES:[DI+32], 0
                Inc     Word Ptr ES:[DI+12]
FCBBlkRead_7A:
                Loop    FCBBlkRead_7

FCBBlkRead_8:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX
                Mov     CX, CS:R_CX

                Jmp     ExitDOS



DoFCBBlkRead_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS





;-----------------------------------------------------------------;
;       Handle FCB Block Write Function Call                      ;
;-----------------------------------------------------------------;

DoFCBBlockWrite:
                Push    AX              ; save registers
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    BP
                Push    ES
                Push    DS


                Mov     CS:OldSP, SP
                Mov     CS:OldSS, SS

                CLI                     ; use our stack
                Mov     SS, CS:OurSS
                Mov     SP, CS:OurSP
                STI

                Mov     CS:R_CX, CX
                Mov     CS:FCBOfs, DX
                Mov     CS:FCBSeg, DS

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD


;
; Find out who's calling us, and for what file.
; Is it one of our skinny files?
;

                Call    SearchFCBTable
                JNC     DoFCBBlkWrite_0  ; it's a skinny file

                Jmp     DoFCBBlkWrite_9  ; not one of ours (let DOS do it)

DoFCBBlkWrite_0:
                Mov     SI, TablePtr
                Mov     AX, FileHandleTbl [SI]
                Mov     CurrHandle, AX
                Call    GetOldPID

                CallDOS GetDTAOp
                Mov     R_DX, BX
                Mov     R_DS, ES

                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBBlkWriteNotExt
                Add     DI, 7
FCBBlkWriteNotExt:
                Mov     CX, Word Ptr ES:[DI+14]
                Mov     Junk, CX
                Mov     AX, R_CX
                Mul     CX
                Mov     R_CX, AX

                Mov     AX, Word Ptr ES:[DI+33]
                Cmp     Word Ptr ES:[DI+14], 64
                JB      FCBBlkWriteRecNLT64

                Xor     DX, DX
                Mov     DL, Byte Ptr ES:[DI+35]
                Jmp     FCBBlkWriteGotRecN

FCBBlkWriteRecNLT64:
                Mov     DX, Word Ptr ES:[DI+35]

FCBBlkWriteGotRecN:
                Mov     BX, Word Ptr ES:[DI+14]
                XOR     CX, CX

                XCHG    AX,SI
                XCHG    AX,DX
                TEST    AX,AX
                JZ      LMul2F
                MUL     BX
LMul2F:         XCHG    AX,CX
                TEST    AX,AX
                JZ      LMul3F
                MUL     SI
                ADD     CX,AX
LMul3F:         XCHG    AX,SI
                MUL     BX
                ADD     DX,CX

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    Put_CX_Bytes_From_DSDX

                Mov     R_AX, 2800h
                Mov     CX, R_CX
                Cmp     BytesMoved, CX
                JE      DoFCBBlkWrite_8

                Mov     R_AX, 2801h

DoFCBBlkWrite_8:
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBBlkWrite_AdjLen
                Add     DI, 7

FCBBlkWrite_AdjLen:
                Mov     AX, Word Ptr Ctrl_FileLen
                Mov     Word Ptr ES:[DI+16], AX
                Mov     AX, Word Ptr Ctrl_FileLen+2
                Mov     Word Ptr ES:[DI+18], AX

DoFCBBlkWrite_8A:
                Mov     AX, BytesMoved
                Xor     DX, DX
                Div     Junk
                Mov     R_CX, AX

                Cmp     Word Ptr ES:[DI+14], 64
                JAE     FCBBlkWrite_8B
                Add     Word Ptr ES:[DI+33], AX
                Adc     Word Ptr ES:[DI+35], 0
                Jmp     FCBBlkWrite_8C

FCBBlkWrite_8B:
                Add     Word Ptr ES:[DI+33], AX
                Adc     Byte Ptr ES:[DI+35], 0

FCBBlkWrite_8C:
                Mov     CX, AX
                JCXZ    FCBBlkWrite_8F
FCBBlkWrite_8D:
                Inc     Byte Ptr ES:[DI+32]
                Cmp     Byte Ptr ES:[DI+32], 128
                JB      FCBBlkWrite_8E

                Mov     Byte Ptr ES:[DI+32], 0
                Inc     Word Ptr ES:[DI+12]
FCBBlkWrite_8E:
                Loop    FCBBlkWrite_8D

FCBBlkWrite_8F:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS              ; request satisfied....
                Pop     ES              ; go back to the application
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX
                Mov     AX, CS:R_AX
                Mov     CX, CS:R_CX

                Jmp     ExitDOS



DoFCBBlkWrite_9:
                CLI                     ; restore user's stack
                Mov     SS, CS:OldSS
                Mov     SP, CS:OldSP
                STI

                Pop     DS
                Pop     ES
                Pop     BP
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Jmp     DefaultDOS



;-----------------------------------------------------------------;
;                                                                 ;
;       Exit back to application, leaving flags/registers         ;
;       in proper state.                                          ;
;                                                                 ;
;-----------------------------------------------------------------;

ExitDOS:
                Cmp     CS:IOFlag, 0
                JNE     ErrorEncountered
                PopF                    ; discard flags
                STI
                CLC                     ; indicate success
                Ret     2


ErrorEncountered:
                Mov     AX, 5

BadDOS:
                PopF                    ; discard flags
                STI
                STC                     ; indicate failure
                Ret     2


DOS_Handler     EndP


;-----------------------------------------------------------------;
;       Check the result of our I/O efforts.                      ;
;-----------------------------------------------------------------;

CheckReadError  Proc    Near
                JC      SayReadError
                Cmp     AX, CX
                JNE     SayReadError
                Jmp     ChkReadExit

SayReadError:
                Cmp     CS:IOFlag, 0
                JNE     ChkReadExit

                Push    AX
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    ES

                Call    SaveLine25
                Push    CS
                Pop     ES
                Mov     IOFlag, 1

                Mov     DX, 1800h
                Mov     DI, Offset ReadErrorMessage
                Mov     CX, LReadError
                Call    AttrCharOut

ReadErrorWait:  Mov     AH, 0
                Int     16h
                Cmp     AL, 0Dh
                JNE     ReadErrorWait
                Call    RestLine25

                Pop     ES
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

ChkReadExit:    Ret
CheckReadError  EndP

;-----------------------------------------------------------------;

CheckWriteError Proc    Near
                JC      SayWriteError
                Cmp     AX, CX
                JNE     SayWriteError
                Jmp     ChkWriteExit

SayWriteError:
                Cmp     CS:IOFlag, 0
                JNE     ChkWriteExit

                Push    AX
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    ES

                Call    SaveLine25
                Push    CS
                Pop     ES
                Mov     IOFlag, 1

                Mov     DX, 1800h
                Mov     DI, Offset WriteErrorMessage
                Mov     CX, LWriteError
                Call    AttrCharOut

WriteErrorWait: Mov     AH, 0
                Int     16h
                Cmp     AL, 0Dh
                JNE     WriteErrorWait
                Call    RestLine25

                Pop     ES
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

ChkWriteExit:    Ret
CheckWriteError  EndP

;-----------------------------------------------------------------;

TooManyCheck    Proc    Near
                Cmp     FileCount, 10
                JBE     TooManyExit

                Push    AX
                Push    BX
                Push    CX
                Push    DX
                Push    SI
                Push    DI
                Push    ES

                Call    SaveLine25
                Push    CS
                Pop     ES
                Mov     IOFlag, 1

                Mov     DX, 1800h
                Mov     DI, Offset TooManyError
                Mov     CX, LTooManyError
                Call    AttrCharOut

TooManyWait:    Mov     AH, 0
                Int     16h
                Cmp     AL, 0Dh
                JNE     TooManyWait
                Call    RestLine25

                Pop     ES
                Pop     DI
                Pop     SI
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                STC
                Ret


TooManyExit:    CLC
                Ret
TooManyCheck    EndP



;-----------------------------------------------------------------;
;       Parse FCB name into NameBuffer, and put                   ;
;       length into CreateLength field.                           ;
;-----------------------------------------------------------------;

ParseFCBName    Proc    Near

                Mov     CreateLength, 0
                Mov     SI, Offset NameBuffer
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     FCBParse_NotExt
                Add     DI, 7

FCBParse_NotExt:
                Mov     AL, Byte Ptr ES:[DI]
                Inc     DI
                Cmp     AL, 0
                JE      FCBParseNoDrive

                Add     AL, "A" - 1

FCBParseDrivePart:
                Mov     Byte Ptr [SI], AL
                Inc     CreateLength
                Inc     SI
                Mov     Byte Ptr [SI], ":"
                Inc     CreateLength
                Inc     SI
                Jmp     FCBParseNamePart

FCBParseNoDrive:
                CallDOS CurrentDiskOp
                Add     AL, "A"
                Jmp     FCBParseDrivePart

FCBParseNamePart:
                Mov     CX, 8
                Push    DI

FCBParseNxtNameChar:
                Mov     AL, Byte Ptr ES:[DI]
                Cmp     AL, " "
                JE      FCBParseGetExt
                Mov     Byte Ptr [SI], AL
                Inc     CreateLength
                Inc     DI
                Inc     SI
                Loop    FCBParseNxtNameChar

FCBParseGetExt:
                Pop     DI
                Add     DI, 8
                Mov     AL, Byte Ptr ES:[DI]
                Cmp     AL, " "
                JE      FCBParseGotName
                Mov     Byte Ptr [SI], "."
                Inc     CreateLength
                Inc     SI
                Mov     Byte Ptr [SI], AL
                Inc     CreateLength
                Inc     DI
                Inc     SI
                Mov     AL, Byte Ptr ES:[DI]
                Cmp     AL, " "
                JE      FCBParseGotName
                Mov     Byte Ptr [SI], AL
                Inc     CreateLength
                Inc     DI
                Inc     SI
                Mov     AL, Byte Ptr ES:[DI]
                Cmp     AL, " "
                JE      FCBParseGotName
                Mov     Byte Ptr [SI], AL
                Inc     CreateLength
                Inc     SI

FCBParseGotName:
                Mov     Byte Ptr [SI], 0
                Push    DS
                Pop     ES

                Ret
ParseFCBName    EndP


;-----------------------------------------------------------------;
;       Get CX bytes into buffer pointed to by DS:DX              ;
;-----------------------------------------------------------------;

Get_CX_Bytes_To_DSDX Proc       Near
;
; See if DeComp-Buffer is for this file/PID and file position
;
                Push    DS
                Pop     ES
                Push    R_CX

                Mov     BytesMoved, 0

DoRead_1A:
                Mov     DI, TablePtr
                Shl     DI, 1
                Mov     AX, Word Ptr FilePosTbl [DI]
                Mov     DX, Word Ptr FilePosTbl [DI+2]
                Mov     Word Ptr CurrFilePos, AX
                Mov     Word Ptr CurrFilePos+2, DX

; Don't go beyond EOF, no matter what the requested bytecount is

                Push    AX
                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Call    GetControlRec
                Pop     AX
                Mov     CX, Word Ptr Ctrl_FileLen
                Mov     BX, Word Ptr Ctrl_FileLen+2

                Cmp     DX, BX
                JA      DoRead_1B
                JB      DoRead_1C
                Cmp     AX, CX
                JB      DoRead_1C

DoRead_1B:      Mov     R_CX, 0
                Jmp     DoRead_6

DoRead_1C:      Sub     CX, AX
                Sbb     BX, DX

                Or      BX, BX
                JNZ     DoRead_1_Continue
                Cmp     CX, R_CX
                JAE     DoRead_1_Continue

                Mov     R_CX, CX

DoRead_1_Continue:
                Cmp     R_CX, 0
                JNE     DoRead_1D
                Jmp     DoRead_6

DoRead_1D:      Mov     BX, MaxBuf
                Div     BX
                Mov     CurrBlock, AX
                Mov     BlockPos, DX

                Cmp     AX, DeCompBlock
                JNE     DoRead_2

                Mov     AX, OldPID
                Cmp     AX, DeCompPID
                JNE     DoRead_2

                Mov     AX, CurrHandle
                Cmp     AX, DeCompHandle
                JNE     DoRead_2

                Jmp     DoRead_3                ; use DeComp Buffer

;
; Read appropriate skinny block and de-compress it.
;
DoRead_2:
                Call    GetBlock
                JNC     DoRead_3

                Jmp     DoRead_6

;
; Transfer decompressed material into application buffer
; (starting at file pos) until either
;       - request is satisfied, or
;       - end of block is encountered.
;

DoRead_3:
                Mov     EndOfBlock, 0   ; default to "we have it all"
                Mov     CX, R_CX        ; set up # bytes to move

                Mov     AX, MaxBuf
                Sub     AX, BlockPos    ; calc # chars left in buffer
                Cmp     AX, CX          ; is it enough?
                JAE     DoRead_3A       ; yes

                Mov     CX, AX          ; only move what we have
                Mov     EndOfBlock, 1   ; signal we'll need next block

DoRead_3A:
                Push    CX
                Mov     SI, Offset DeCompBuffer
                Add     SI, BlockPos
                LES     DI, ApplBufferPtr
        Rep     MovSB
                Mov     R_DX, DI
                Pop     CX

                Push    DS
                Pop     ES

;
; if we encountered end-of-block before, go back to finish the job.
;
DoRead_4:
                Add     BytesMoved, CX          ; what we've done so far
                Sub     R_CX, CX                ; remainder to move

                Cmp     EndOfBlock, 1           ; need to get next block?
                JNE     DoRead_6                ; no

                Mov     BlockPos, 0
                Inc     CurrBlock
                Jmp     DoRead_2

;
; update file-position information
;
DoRead_6:
                Mov     CX, BytesMoved
                Add     Word Ptr CurrFilePos, CX
                Adc     Word Ptr CurrFilePos+2, 0

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     AX, Word Ptr CurrFilePos
                Mov     DX, Word Ptr CurrFilePos+2
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Pop     R_CX
                Ret
Get_CX_Bytes_To_DSDX EndP


;-----------------------------------------------------------------;
;       Put CX bytes from DS:DX buffer to disk                    ;
;-----------------------------------------------------------------;

Put_CX_Bytes_From_DSDX Proc     Near
                Push    DS
                Pop     ES
                Push    R_CX

                Mov     BytesMoved, 0

                Mov     DI, TablePtr
                Shl     DI, 1
                Mov     AX, Word Ptr FilePosTbl [DI]
                Mov     DX, Word Ptr FilePosTbl [DI+2]
                Mov     Word Ptr CurrFilePos, AX
                Mov     Word Ptr CurrFilePos+2, DX

                Mov     BX, MaxBuf
                Div     BX
                Mov     CurrBlock, AX
                Mov     BlockPos, DX

                Cmp     AX, DeCompBlock
                JNE     DoWrite_2

                Mov     AX, OldPID
                Cmp     AX, DeCompPID
                JNE     DoWrite_2

                Mov     AX, CurrHandle
                Cmp     AX, DeCompHandle
                JNE     DoWrite_2

                Jmp     DoWrite_4                ; use DeComp Buffer

;
; is current file position anywhere inside the file already?
;

DoWrite_2:
                Call    GetBlock
                JNC     DoWrite_4

;
; fill decomp buffer with nulls
;

DoWrite_3:
                Mov     DI, Offset DeCompBuffer
                Mov     AX, 0
                Mov     CX, (MaxBuf/2)
        Rep     StoSW

;
; merge material to be written into DeComp Buffer
;

DoWrite_4:
                Mov     EndOfBlock, 0           ; default to "it fits"
                Mov     CX, R_CX                ; # bytes to write

                Mov     AX, MaxBuf
                Sub     AX, BlockPos            ; bufsize - current position
                Cmp     AX, CX                  ; # chars left in buffer
                JAE     DoWrite_4A              ; buffer is large enough

                Mov     CX, AX                  ; only move what we can
                Mov     EndOfBlock, 1           ; signal "we'll need next block"

DoWrite_4A:
                Cmp     R_CX, 0
                JE      DoWriteTruncate

                Mov     DeCompDirty, 1
                Push    CX
                Mov     DI, Offset DeCompBuffer
                Add     DI, BlockPos
                LDS     SI, ApplBufferPtr
        Rep     MovSB
                Pop     CX

                Push    ES
                Pop     DS
                Mov     R_DX, SI

;
; update the stats.  do we need another block?
;

DoWrite_5:
                Add     BytesMoved, CX
                Sub     R_CX, CX                ; keep track of partial blks

                Cmp     EndOfBlock, 1           ; need to continue into nxt blk?
                JNE     DoWrite_6               ; no

                Mov     BlockPos, 0
                Inc     CurrBlock

                Jmp     DoWrite_2


DoWriteTruncate:
                Cmp     Word Ptr CurrFilePos, 0
                JNE     DoWriteTrunc2
                Cmp     Word Ptr CurrFilePos+2, 0
                JNE     DoWriteTrunc2

                Call    WriteInitControl
                Jmp     DoWrite_6

DoWriteTrunc2:
                Mov     CX, MaxBuf
                Sub     CX, BlockPos
                Mov     DI, Offset DeCompBuffer
                Add     DI, BlockPos
                Xor     AX, AX
        Rep     StoSB
                Mov     DeCompDirty, 1

                Mov     DI, Offset Loc_Len_Info
                Mov     AX, 6
                Mov     CX, CurrBlock
                Sub     CX, PointersStart
                Inc     CX
                Mul     CX
                Add     DI, AX
                Mov     AL, 0FFh
                Mov     CX, Offset EndOfCtrlRec
                Sub     CX, DI
        Rep     StoSB
                Mov     PtrsDirty, 1

                Mov     AX, Word Ptr CurrFilePos
                Mov     DX, Word Ptr CurrFilePos+2

                Jmp     DoWrite_7

;
; update file-position information
;
DoWrite_6:
                Mov     CX, BytesMoved
                Add     Word Ptr CurrFilePos, CX
                Adc     Word Ptr CurrFilePos+2, 0

                Mov     SI, TablePtr
                Shl     SI, 1
                Mov     AX, Word Ptr CurrFilePos
                Mov     DX, Word Ptr CurrFilePos+2
                Mov     Word Ptr FilePosTbl [SI], AX
                Mov     Word Ptr FilePosTbl [SI+2], DX

                Call    AlignDupedFiles

                Cmp     DX, Word Ptr Ctrl_FileLen+2
                JB      DoWrite_8
                JA      DoWrite_7
                Cmp     AX, Word Ptr Ctrl_FileLen
                JBE     DoWrite_8

DoWrite_7:
                Mov     Word Ptr Ctrl_FileLen, AX    ; new "virtual"
                Mov     Word Ptr Ctrl_FileLen+2, DX  ; file length
                Mov     CtrlDirty, 1

DoWrite_8:
                Pop     R_CX
                Ret
Put_CX_Bytes_From_DSDX EndP


;-----------------------------------------------------------------;
;       See if FCB name is in FCBTable                            ;
;-----------------------------------------------------------------;

SearchFCBTable  Proc    Near
                LES     DI, FCBPtr
                Cmp     Byte Ptr ES:[DI], 0FFh
                JNE     SearchFCB_1
                Add     DI, 7
SearchFCB_1:
                Mov     SI, Offset FCBTable
                Mov     AX, 0

FCBNextNmEntry:
                Push    SI
                Push    DI
                Mov     CX, 6
        RepE    CmpSW
                Pop     DI
                Pop     SI
                JNE     BumpToNextFCBName

                Push    DS
                Pop     ES
                Mov     FCBTablePtr, SI
                Shl     AX, 1
                Mov     TablePtr, AX
                CLC
                Ret

BumpToNextFCBName:
                Add     SI, 12
                Inc     AX
                Cmp     AX, MaxHandles
                JB      FCBNextNmEntry

                Push    DS
                Pop     ES
                STC
                Ret
SearchFCBTable  EndP


;-----------------------------------------------------------------;
;       Put message pointed to by ES:DI out to the screen         ;
;       on line 25.  Use an attribute of black-on-white.          ;
;       Length of message is in CX.  Row/Col in DX.               ;
;-----------------------------------------------------------------;

AttrCharOut     Proc    Near
ACO_Next:       JCXZ    ACO_Exit
                Mov     AH, 2
                Mov     BH, 0
                Int     10h

                Mov     AL, Byte Ptr ES:[DI]
                Push    CX
                Mov     AH, 9
                Mov     BX, 0070h
                Mov     CX, 1
                Int     10h
                Pop     CX

                Dec     CX
                Inc     DI
                Inc     DL
                Jmp     ACO_Next

ACO_Exit:       Ret
AttrCharOut     EndP


;-----------------------------------------------------------------;
;       Save any text on screen line 25.                          ;
;-----------------------------------------------------------------;

SaveLine25      Proc    Near
                Mov     AH, 3
                Mov     BH, 0
                Int     10h
                Mov     CPosSave, DX
                Mov     CTypSave, CX

                Mov     SI, 0
                Mov     DX, 1800h

GetFromScrn:
                Push    SI
                Mov     AH, 2
                Mov     BH, 0
                Int     10h
                Mov     AH, 8
                Mov     BH, 0
                Int     10h
                Pop     SI
                Mov     Word Ptr ScreenSave [SI], AX
                Inc     DX
                Inc     SI
                Inc     SI
                Cmp     DX, 184Fh
                JNE     GetFromScrn

                Ret
SaveLine25      EndP




;-----------------------------------------------------------------;
;       Restore text on screen line 25.                           ;
;-----------------------------------------------------------------;

RestLine25      Proc    Near
                Mov     SI, 0
                Mov     DX, 1800h

PutToScrn:
                Push    SI
                Mov     AH, 2
                Mov     BH, 0
                Int     10h
                Pop     SI

                Mov     AX, Word Ptr ScreenSave [SI]
                Push    SI
                Mov     BL, AH
                Mov     BH, 0
                Mov     CX, 1
                Mov     AH, 9
                Int     10h
                Pop     SI
                Inc     DX
                Inc     SI
                Inc     SI
                Cmp     DX, 184Fh
                JNE     PutToScrn

                Mov     AH, 1
                Mov     CX, CTypSave
                Int     10h
                Mov     DX, CPosSave
                Mov     BH, 0
                Mov     AH, 2
                Int     10h

                Ret
RestLine25      EndP

;-----------------------------------------------------------------;
;                                                                 ;
;       Get a block of skinny material & decompress it            ;
;                                                                 ;
;-----------------------------------------------------------------;

GetBlock        Proc    Near
                Call    PutBlock

                Mov     AdvancePtr, 0
                Mov     AX, CurrBlock
                Mov     DeCompBlock, AX
                Mov     AX, OldPID
                Mov     DeCompPID, AX
                Mov     AX, CurrHandle
                Mov     DeCompHandle, AX

                Mov     AX, CurrHandle
                Mov     GetCtrlHandle, AX
                Mov     GetPtrsHandle, AX
                Mov     AX, OldPID
                Mov     GetCtrlPID, AX
                Mov     GetPtrsPID, AX
                Call    GetControlRec           ; for filelength

                Mov     AX, CurrBlock
                Mov     PointerBlock, AX
                Call    GetPointerRec           ; based on CurrBlock

GetBlock_1:
                Mov     BX, Offset Loc_Len_Info ; get block position
                Mov     AX, 6
                Mov     SI, CurrBlock
                Sub     SI, PointersStart
                Mul     SI
                Add     BX, AX

                Mov     DX, Word Ptr [BX]       ; location low word
                Mov     CX, Word Ptr [BX+2]     ; location high word
                Mov     SI, Word Ptr [BX+4]     ; length

                Cmp     SI, 0FFFFh              ; valid entry?
                JNE     GetBlock_2              ; yes

BlockNotFound:
                STC
                Ret

; - - - - - - - - - - - - - - - - - - - - - - - -
GetBlock_2:
                Mov     AX, 0
                Mov     BX, CurrHandle
                CallDOS SeekOp                  ; seek to skinny block

                Mov     CX, SI                  ; remember length
                Mov     BX, CurrHandle          ; read skinny block
                Mov     DX, Offset DeCompBuffer
                CallDOS ReadOp
                Call    CheckReadError

                Mov     DI, Offset IOBuffer
                Add     DI, AdvancePtr
                Mov     SI, Offset DeCompBuffer+6
                Sub     CX, 6
                Add     AdvancePtr, CX
        Rep     MovSB

;
; now get any "extents" that belong to this compressed material
;

LookAtLink:
                Cmp     ILinkLen, 0FFFFh        ; last in chain?
                JE      DeCompressThisBlock     ; yes

                Mov     CX, Word Ptr ILinkPtr+2
                Mov     DX, Word Ptr ILinkPtr
                Mov     SI, ILinkLen

                Jmp     GetBlock_2

DecompressThisBlock:
                Mov     Prefix_Code, 0
                Mov     Free_Code, First_Free
                Mov     Max_Code, K512
                Mov     NBits, K9
                Mov     K, 0
                Mov     Bit_Offset, 0
                Mov     Input_Offset, 0
                Mov     Input_Size, MaxBuf
                Mov     Cur_Code, 0
                Mov     Old_Code, 0
                Mov     In_Code, 0
                Mov     Stack_Count, 0
                Mov     Fin_Char, 0
                Mov     Output_Offset, 0

                Mov     DI, Offset Hash
                Mov     CX, (maxmax * 5) / 2
                Xor     AX, AX
        Rep     StoSW

                Call    DeCompress              ; IOBuffer --> DeCompBuffer

                CLC
                Ret
GetBlock        EndP


;-----------------------------------------------------------------;
;       Compress DeCompBuffer into IOBuffer and write             ;
;       IOBuffer out to disk.                                     ;
;-----------------------------------------------------------------;

PutBlock        Proc    Near
                Cmp     DeCompDirty, 1
                JE      DoWriteTheBlock

                Ret

DoWriteTheBlock:
                Mov     Prefix_Code, 0
                Mov     Free_Code, 0
                Mov     Max_Code, K512
                Mov     NBits, K9
                Mov     K, 0
                Mov     Bit_Offset, 0
                Mov     Input_Offset, 0
                Mov     Input_Size, MaxBuf
                Mov     Cur_Code, 0
                Mov     Old_Code, 0
                Mov     In_Code, 0
                Mov     Stack_Count, 0
                Mov     Fin_Char, 0
                Mov     Output_Offset, 0

                Mov     DI, Offset Hash
                Mov     CX, (maxmax * 5) / 2
                Xor     AX, AX
        Rep     StoSW

                Call    Compress                ; DeCompBuf --> IOBuf+6

                Mov     AX, DeCompHandle
                Mov     GetCtrlHandle, AX
                Mov     GetPtrsHandle, AX
                Mov     AX, DeCompPID
                Mov     GetCtrlPID, AX
                Mov     GetPtrsPID, AX
                Call    GetControlRec

                Mov     AX, DeCompBlock
                Mov     PointerBlock, AX
                Call    GetPointerRec

                Mov     BX, Offset Loc_Len_Info ; get block position
                Mov     AX, 6
                Mov     SI, DeCompBlock
                Sub     SI, PointersStart
                Mul     SI
                Add     BX, AX
                Mov     PtrRecSegment, BX

                Mov     DX, Word Ptr [BX]       ; location low word
                Mov     CX, Word Ptr [BX+2]     ; location high word
                Mov     SI, Word Ptr [BX+4]     ; length

                Mov     Word Ptr CurrPtr, DX
                Mov     Word Ptr CurrPtr+2, CX
                Mov     CurrLen, SI

                Mov     AX, Offset IOBuffer+6
                Mov     AdvancePtr, AX
                Mov     AX, CompressLength
                Mov     LenToWrite, AX

PutBlock_1:
                Cmp     LenToWrite, 0
                JNE     PutBlock_2

PutBlockExit:
                Mov     DeCompDirty, 0
                Ret


PutBlock_2:     Cmp     Word Ptr CurrPtr+2, 0FFFFh
                JE      PutBlock_3

                Sub     CurrLen, 6

                Mov     DX, Word Ptr CurrPtr
                Mov     CX, Word Ptr CurrPtr+2
                Mov     BX, DeCompHandle
                Mov     AL, 0
                CallDOS SeekOp

                Mov     BX, DeCompHandle
                Mov     CX, 6
                Mov     DX, Offset IOBuffer
                CallDOS ReadOp
                Call    CheckReadError

                Mov     AX, Word Ptr OLinkPtr
                Mov     Word Ptr NextPtr, AX
                Mov     AX, Word Ptr OLinkPtr+2
                Mov     Word Ptr NextPtr+2, AX
                Mov     AX, OLinkLen
                Mov     NextLen, AX

                Jmp     PutBlock_4

PutBlock_3:
                Mov     CX, 0
                Mov     DX, CX
                Mov     AL, 2
                Mov     BX, DeCompHandle
                CallDOS SeekOp

                Mov     CX, DX
                Mov     DX, AX
                Mov     Word Ptr CurrPtr, DX
                Mov     Word Ptr CurrPtr+2, CX
                Mov     AX, LenToWrite
                Mov     CurrLen, AX

                Mov     BX, PtrRecSegment
                Cmp     Word Ptr [BX+2], 0FFFFh
                JNE     PutBlock_3A

                Mov     Word Ptr [BX], DX
                Mov     Word Ptr [BX+2], CX
                Add     AX, 6
                Mov     Word Ptr [BX+4], AX
                Mov     PtrsDirty, 1
                Jmp     PutBlock_3B

PutBlock_3A:
                Mov     DX, Word Ptr PrevPtr
                Mov     CX, Word Ptr PrevPtr+2
                Mov     BX, DeCompHandle
                Mov     AL, 0
                CallDOS SeekOp

                Mov     AX, Word Ptr CurrPtr
                Mov     Word Ptr OLinkPtr, AX
                Mov     AX, Word Ptr CurrPtr+2
                Mov     Word Ptr OLinkPtr+2, AX
                Mov     AX, CurrLen
                Add     AX, 6
                Mov     OLinkLen, AX

                Mov     BX, DeCompHandle
                Mov     CX, 6
                Mov     DX, Offset IOBuffer
                CallDOS WriteOp
                Call    CheckWriteError

PutBlock_3B:
                Mov     Word Ptr NextPtr, 0FFFFh
                Mov     Word Ptr NextPtr+2, 0FFFFh
                Mov     NextLen, 0FFFFh


PutBlock_4:     Mov     DX, Word Ptr CurrPtr
                Mov     Word Ptr PrevPtr, DX
                Mov     CX, Word Ptr CurrPtr+2
                Mov     Word Ptr PrevPtr+2, CX
                Mov     BX, DeCompHandle
                Mov     AL, 0
                CallDOS SeekOp

                Mov     SI, AdvancePtr
                Mov     AX, Word Ptr NextPtr
                Mov     Word Ptr [SI-6], AX
                Mov     AX, Word Ptr NextPtr+2
                Mov     Word Ptr [SI-4], AX
                Mov     AX, NextLen
                Mov     Word Ptr [SI-2], AX

                Mov     AX, LenToWrite
                Cmp     AX, CurrLen
                JAE     PutBlock_5

                Mov     CurrLen, AX

PutBlock_5:
                Mov     DX, AdvancePtr
                Sub     DX, 6
                Mov     CX, CurrLen
                Add     CX, 6
                Mov     BX, DeCompHandle
                CallDOS WriteOp
                Call    CheckWriteError

                Mov     AX, CurrLen
                Sub     LenToWrite, AX
                Add     AdvancePtr, AX

                Mov     DX, Word Ptr NextPtr
                Mov     Word Ptr CurrPtr, DX
                Mov     CX, Word Ptr NextPtr+2
                Mov     Word Ptr CurrPtr+2, CX
                Mov     AX, NextLen
                Mov     CurrLen, AX

                Jmp     PutBlock_1

PutBlock        EndP


;-----------------------------------------------------------------;
;       Get the control record, if necessary                      ;
;-----------------------------------------------------------------;

GetControlRec   Proc    Near
                Push    AX
                Push    BX
                Push    CX
                Push    DX

                Mov     AX, GetCtrlPID
                Cmp     AX, CtrlPID
                JNE     ReadTheCtrlRec
                Mov     AX, GetCtrlHandle
                Cmp     AX, CtrlHandle
                JNE     ReadTheCtrlRec

                Jmp     AlreadyHaveCtrl

ReadTheCtrlRec:
                Call    WriteTheCtrlRec

                Mov     AX, GetCtrlHandle
                Mov     CtrlHandle, AX
                Mov     AX, GetCtrlPID
                Mov     CtrlPID, AX

                Mov     CX, 0           ; get control record
                Mov     DX, CX          ; from beginning of file
                Mov     AX, CX
                Mov     BX, CtrlHandle
                CallDOS SeekOp

                Mov     CX, CtrlSize
                Mov     BX, CtrlHandle
                Mov     DX, Offset CtrlBuffer
                CallDOS ReadOp
                Call    CheckReadError

AlreadyHaveCtrl:
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Ret
GetControlRec   EndP


;-----------------------------------------------------------------;
;       Write the control record to the beginning of the file     ;
;-----------------------------------------------------------------;

WriteTheCtrlRec Proc    Near
                Cmp     CtrlDirty, 0
                JE      WriteCtrlExit

                Push    AX
                Push    BX
                Push    CX
                Push    DX

                Mov     CX, 0                   ; seek to beginning of file
                Mov     DX, CX
                Mov     AL, 0
                Mov     BX, CtrlHandle
                CallDOS SeekOp

                Mov     BX, CtrlHandle          ; re-write control record
                Mov     DX, Offset CtrlBuffer
                Mov     CX, CtrlSize
                CallDOS WriteOp
                Call    CheckWriteError

                Mov     CtrlDirty, 0

                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

WriteCtrlExit:
                Ret
WriteTheCtrlRec EndP


;-----------------------------------------------------------------;
;       Get the pointer record that corresponds to the            ;
;       block # in PointerBlock.                                  ;
;-----------------------------------------------------------------;

GetPointerRec   Proc    Near
                Push    AX
                Push    BX
                Push    CX
                Push    DX

                Mov     BX, GetPtrsPID
                Cmp     BX, PtrsPID
                JNE     Read1stPtrsRec
                Mov     BX, GetPtrsHandle
                Cmp     BX, PtrsHandle
                JNE     Read1stPtrsRec

                Jmp     GetRightPointers

Read1stPtrsRec:
                Call    WritePointerRec

                Mov     AX, GetPtrsHandle
                Mov     PtrsHandle, AX
                Mov     AX, GetPtrsPID
                Mov     PtrsPID, AX

                Mov     CX, 0           ; get first pointers record
                Mov     DX, 16
                Mov     AX, 0
                Mov     BX, PtrsHandle
                CallDOS SeekOp
                Mov     Word Ptr PtrsFilePos, AX
                Mov     Word Ptr PtrsFilePos+2, DX

                Mov     CX, PtrsSize
                Mov     BX, PtrsHandle
                Mov     DX, Offset Ctrl_Pointers
                CallDOS ReadOp
                Call    CheckReadError

                Mov     PointersStart, 0
                Mov     PointersEnd,   NumPtrs-1

GetRightPointers:
                Mov     AX, PointerBlock
                Cmp     AX, PointersStart
                JB      ChainBack
                Jmp     LastPtrTest

ChainBack:
                Call    WritePointerRec
                Mov     CX, Word Ptr Ctrl_Prev+2      ; chain backwards
                Mov     DX, Word Ptr Ctrl_Prev
                Mov     BX, PtrsHandle
                Mov     AL, 0
                CallDOS SeekOp
                Mov     DX, Offset Ctrl_Pointers
                Mov     BX, PtrsHandle
                Mov     CX, PtrsSize
                CallDOS ReadOp
                Call    CheckReadError

                Sub     PointersStart, NumPtrs
                Sub     PointersEnd,   NumPtrs
                Jmp     GetRightPointers

LastPtrTest:
                Mov     AX, PointerBlock
                Cmp     AX, PointersEnd
                JA      ChainForwards
                Jmp     GotRightPointers

ChainForwards:
                Call    WritePointerRec
                Mov     CX, Word Ptr Ctrl_Next+2      ; chain forwards
                Mov     DX, Word Ptr Ctrl_Next

                Cmp     CX, 0
                JNE     ChainNext
                Cmp     DX, 0
                JNE     ChainNext
                Jmp     CreateNewPointers

ChainNext:
                Mov     BX, PtrsHandle
                Mov     AL, 0
                CallDOS SeekOp
                Mov     Word Ptr PtrsFilePos, AX
                Mov     Word Ptr PtrsFilePos+2, DX

                Mov     DX, Offset Ctrl_Pointers
                Mov     BX, PtrsHandle
                Mov     CX, PtrsSize
                CallDOS ReadOp
                Call    CheckReadError

                Add     PointersStart, NumPtrs
                Add     PointersEnd,   NumPtrs
                Jmp     GetRightPointers


CreateNewPointers:
                Push    Word Ptr PtrsFilePos
                Push    Word Ptr PtrsFilePos+2

                Mov     CX, 0                   ; seek to end of file
                Mov     DX, CX
                Mov     AL, 2
                Mov     BX, PtrsHandle
                CallDOS SeekOp
                Mov     Word Ptr Ctrl_Next+2, DX
                Mov     Word Ptr Ctrl_Next, AX
                Mov     PtrsDirty, 1
                Call    WritePointerRec

                Mov     DI, Offset Ctrl_Pointers
                Mov     AX, 0
                Mov     CX, 8
        Rep     StoSW
                Mov     AX, 0FFFFh
                Mov     CX, (PtrsSize / 2) - 8
        Rep     StoSW

                Pop     Word Ptr Ctrl_Prev+2
                Pop     Word Ptr Ctrl_Prev

                Mov     AX, GetPtrsHandle
                Mov     PtrsHandle, AX
                Mov     AX, GetPtrsPID
                Mov     PtrsPID, AX

                Mov     CX, 0                   ; seek to end of file
                Mov     DX, CX
                Mov     AL, 2
                Mov     BX, PtrsHandle
                CallDOS SeekOp

                Mov     Word Ptr PtrsFilePos, AX
                Mov     Word Ptr PtrsFilePos+2, DX

                Add     PointersStart, NumPtrs
                Add     PointersEnd,   NumPtrs
                Mov     PtrsDirty, 1
                Call    WritePointerRec

GotRightPointers:
                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

                Ret
GetPointerRec   EndP

;-----------------------------------------------------------------;
;       Write the current pointer record.                         ;
;-----------------------------------------------------------------;

WritePointerRec Proc    Near
                Cmp     PtrsDirty, 0
                JE      WritePtrsExit

                Push    AX
                Push    BX
                Push    CX
                Push    DX

                Mov     CX, Word Ptr PtrsFilePos+2
                Mov     DX, Word Ptr PtrsFilePos
                Mov     AX, 0
                Mov     BX, PtrsHandle
                CallDOS SeekOp

                Mov     BX, PtrsHandle
                Mov     DX, Offset Ctrl_Pointers
                Mov     CX, PtrsSize
                CallDOS WriteOp
                Call    CheckWriteError

                Mov     PtrsDirty, 0

                Pop     DX
                Pop     CX
                Pop     BX
                Pop     AX

WritePtrsExit:
                Ret
WritePointerRec EndP


;-----------------------------------------------------------------;
;       if handled dup'd, make file pos the same for both.        ;
;-----------------------------------------------------------------;

AlignDupedFiles Proc    Near
                Push    AX
                Push    BX
                Push    SI
                Push    DI

                Mov     SI, TablePtr
                Mov     DI, DupeTable [SI]
                Cmp     DI, 0FFFFh
                JE      AlignExit
                Shl     DI, 1
                Shl     SI, 1
                Mov     AX, Word Ptr FilePosTbl [SI]
                Mov     BX, Word Ptr FilePosTbl+2 [SI]
                Mov     Word Ptr FilePosTbl [DI], AX
                Mov     Word Ptr FilePosTbl+2 [DI], BX
AlignExit:
                Pop     DI
                Pop     SI
                Pop     BX
                Pop     AX
                Ret
AlignDupedFiles EndP


;-----------------------------------------------------------------;
;       Get a buffer of Diet.Dir bytes into                       ;
;       'ScreenSave'.                                             ;
;-----------------------------------------------------------------;

FGetBuff        Proc    Near
FGB1:           Mov     SI, fbufndx
                Cmp     SI, fbufbytes
                JAE     FGB2

                Mov     AL, ScreenSave[SI]
                Inc     fbufndx
                Jmp     Short FGB_Exit

FGB2:           Mov     DX, Offset ScreenSave
                Mov     BX, DietDirHandle
                Mov     CX, 160
                CallDOS ReadOp
                JC      FGB_Eof
                Cmp     AX, 0
                JE      FGB_Eof

                Mov     fbufbytes, AX
                Mov     fbufndx, 0
                Jmp     Short FGB1

FGB_Eof:        Mov     fbufndx, MaxTextBuf
                Mov     AL, 0FFh

FGB_Exit:       Ret
FGetBuff        EndP


;-----------------------------------------------------------------;
;                                                                 ;
;       Switch DTAs before parsing Diet.Dir                       ;
;                                                                 ;
;-----------------------------------------------------------------;

UseOurDTA       Proc    Near
                CallDOS GetDTAOp
                Mov     OldDTAOfs, BX
                Mov     OldDTASeg, ES
                Push    DS
                LDS     DX, OurDTA
                CallDOS SetDTAOp
                Pop     DS
                Push    DS
                Pop     ES
                Ret
UseOurDTA       EndP


SetOldDTA       Proc    Near
                Push    DS
                LDS     DX, OldDTA
                CallDOS SetDTAOp
                Pop     DS
                Ret
SetOldDTA       EndP


;-----------------------------------------------------------------;
;       Search 'DIET.DIR' for this file name                      ;
;       Return Carry-True if file not found                       ;
;-----------------------------------------------------------------;

SearchDietDir   Proc    Near
                Call    UseOurDTA
                Call    SetOurPID
                Mov     DietEOF, 0
                Call    Parse_DS_DX_Name

                Call    TooManyCheck
                JNC     Search_0
                Jmp     Short JustGoAway

Search_0:
                Mov     DX, Offset DietPath
                Mov     AL, RD_ONLY
                CallDOS OpenOp
                JNC     Search_1

JustGoAway:
                Call    SetOldDTA
                Call    SetOldPID
                STC
                Ret

Search_1:
                Mov     DietDirHandle, AX
                Mov     fbufbytes, 0
                Mov     fbufndx, MaxTextBuf

Search_2A:
                Mov     AL, 0
                Mov     CX, MaxName
                Mov     DI, Offset NameBuffer
        Rep     StoSB
                Mov     CharPos, 0

Search_2:
                Call    FGetBuff                ; get a byte of DietDir
                                                ; into AL
Search_TestEOF:
                Cmp     AL, 0FFh                ; EOF?
                JNE     Search_3

                Mov     DietEOF, 1            ; no more input
                Jmp     Search_4                ; go look at last name

Search_3:
                Cmp     AL, 10
                JE      Search_2
                Cmp     AL, 26
                JE      Search_2

                Mov     SI, CharPos
                Cmp     AL, 13
                JE      Search_3C

                Mov     NameBuffer[SI], AL
                Cmp     CharPos, MaxName-1
                JE      Search_4

                Inc     CharPos                 ; go get next char
                Jmp     Search_2

Search_3C:
                Mov     NameBuffer[SI], 0
                Jmp     Search_4


;- - - - - - - - - - - - - - - - - - - - - - - 

GoBackToSearch_2A:
                Jmp     Search_2A               ; a local jumping place

Search_4:
                Mov     AX, CharPos
                XChg    AH, AL
                Or      AX, DietEOF
                Cmp     AX, 0001h               ; EOF and empty line?
                JE      Search_9
                Cmp     AH, 0                   ; empty line?
                JE      GoBackToSearch_2A

                Cmp     NameBuffer, ' '         ; if first char is blank,
                JE      GoBackToSearch_2A       ; ignore line
                Cmp     NameBuffer, ';'         ; do the same if it starts
                JE      GoBackToSearch_2A       ; with a semicolon

                Call    IsThisIt                ; is this line of Diet.Dir
                JNC     Search_5                ; the filename being created?

                Cmp     DietEOF, 1              ; are we all done looking?
                JE      Search_9

                Jmp     Search_2A               ; no, go read another line

Search_5:
                Mov     BX, DietDirHandle
                CallDOS CloseOp
                Call    SetOldDTA
                Call    SetOldPID
                CLC
                Ret

Search_9:
                Mov     BX, DietDirHandle
                CallDOS CloseOp
                Call    SetOldDTA
                Call    SetOldPID
                STC
                Ret
SearchDietDir EndP


;-----------------------------------------------------------------;
;       Turn DS:DX path/file name into something                  ;
;       we can compare against.  Put resulting filename           ;
;       in CreateName and put length in CreateLength.             ;
;-----------------------------------------------------------------;

Parse_DS_DX_Name Proc   Near
                Push    DS
                Pop     ES
                Mov     AL, 0
                Mov     CX, MaxName
                Mov     DI, Offset CreateName
        Rep     StoSB

                LES     DI, CreatePtr           ; calc length of DSDX name
                Mov     BX, DI
                Mov     CX, MaxName
                Mov     AL, 0
        RepNE   ScaSB
                Sub     DI, BX
                Mov     CreateLength, DI

                Mov     SI, Offset CreateName

                LES     DI, CreatePtr           ; old ds:dx pointer
                Cmp     Byte Ptr ES:[DI+1], ':'
                JE      ParseDSDX_Drive

                CallDOS CurrentDiskOp           ; generate <d>:
                Add     AL, "A"
                Mov     AH, ":"
                Jmp     ParseDSDX_GetName

ParseDSDX_Drive:
                Mov     AX, Word Ptr ES:[DI]    ; pick up <d>:
                Inc     DI
                Inc     DI
                Dec     CreateLength
                Dec     CreateLength
                Cmp     AL, '_'
                JBE     ParseDSDX_GetName
                And     AL, '_'

ParseDSDX_GetName:
                Mov     Word Ptr CreateName, AX
                Inc     SI
                Inc     SI

                Push    ES                      ; save modified CreatePtr
                Push    DI

                Cmp     Byte Ptr ES:[DI], '\'   ; do we need cwd?
                JE      ParseDSDX_DoRemainder   ; no

                Push    DS  
                Pop     ES

                Mov     Byte Ptr [SI], '\'
                Inc     SI
                Mov     DL, Byte Ptr CreateName
                Sub     DL, '@'
                CallDOS GetCurrDir
                Mov     DI, Offset CreateName
                Mov     CX, MaxName
                Mov     AL, 0
        RepNE   ScaSB
                Dec     DI
                Mov     SI, DI
                Cmp     Byte Ptr [SI-1], '\'
                JE      ParseDSDX_DoRemainder
                Mov     Byte Ptr [SI], '\'
                Inc     SI

ParseDSDX_DoRemainder:
                Mov     CX, CreateLength
                Mov     AX, DS
                Mov     BX, SI
                Pop     SI              ; recover modified CreatePtr
                Pop     DS
                Mov     ES, AX
                Mov     DI, BX
        Rep     MovSB
                Mov     Byte Ptr ES:[DI], 0

                Push    CS              ; restore addressability
                Pop     DS
                Push    DS
                Pop     ES

                Mov     DI, Offset CreateName
                Mov     BX, DI
                Mov     CX, MaxName
                Mov     AL, 0
        RepNE   ScaSB
                Mov     CX, DI
                Dec     CX
                Sub     CX, BX
                Mov     CreateLength, CX
                STD
                Mov     CX, MaxName
                Mov     AL, '\'
        RepNE   ScaSB
                CLD
                Inc     DI
                Inc     DI
                Sub     DI, BX
                Mov     DirLength, DI

                Ret
Parse_DS_DX_Name EndP

;-----------------------------------------------------------------;
;       See if NameBuffer (from DIET.DIR) is the same as          ;
;       the filename just created.  Return Carry-Clear if equal.  ;
;-----------------------------------------------------------------;

IsThisIt        Proc    Near
                Mov     DI, Offset NameBuffer
                Mov     SI, Offset CreateName
                Mov     CX, DirLength

; directory names must match exactly

fmd1:           mov     al,byte ptr [si]
                cmp     al,'_'
                jbe     fmd2
                and     al,'_'

fmd2:           mov     bl,byte ptr [di]
                cmp     bl,'_'
                jbe     fmd3
                and     bl,'_'

fmd3:           cmp     al,bl
                je      fmd4

                cmp     bl, '='
                jne     no_dir_match

                clc
                jmp     fm1

no_dir_match:   stc
                jmp     fm1

fmd4:           inc     si
                inc     di
                loop    fmd1


; do the filename portion separately from the extension

fm2:            mov     al,byte ptr [si]
                cmp     al,'\'
                je      fm11
                cmp     al,'_'
                jbe     fm3
                and     al,'_'

fm3:            mov     bl,byte ptr [di]
                cmp     bl,'\'
                je      fm11
                cmp     bl,'_'
                jbe     fm4
                and     bl,'_'

fm4:            cmp     bl,'*'
                jne     fm5
                inc     di

fm6:            cmp     byte ptr [si],0
                je      fm8
                cmp     byte ptr [si],'.'
                je      fm8
                inc     si
                jmp     short fm6

fm5:            cmp     al,0
                je      fm8
                cmp     bl,0
                je      fm8
                cmp     al,'.'
                je      fm8
                cmp     bl,'.'
                je      fm8

fm9:            cmp     al,bl
                je      fm12
                cmp     bl,'?'
                jne     fm11

fm12:           inc     si
                inc     di
                jmp     fm2

fm11:           stc
                jmp     fm1


; now do the extension

fm8:            mov     al,byte ptr [si]
                cmp     al,'_'
                jbe     fm13
                and     al,'_'

fm13:           mov     bl,byte ptr [di]
                cmp     bl,'_'
                jbe     fm14
                and     bl,'_'

fm14:           cmp     al,'.'
                jne     fm15
                inc     si
                jmp     short fm8

fm15:           cmp     bl,'.'
                jne     fm16
                inc     di
                jmp     short fm8

fm16:           cmp     bl,'*'
                jne     fm17
                clc
                jmp     short fm1

fm17:           cmp     al,0
                jne     fm18
                cmp     bl,0
                jne     fm19
                clc
                jmp     short fm1
                jmp     short fm18

fm19:           stc
                jmp     short fm1

fm18:           cmp     bl,0
                jne     fm21
                stc
                jmp     short fm1

fm21:           cmp     al,bl
                je      fm23
                cmp     bl,'?'
                jne     fm22

fm23:           inc     si
                inc     di
                jmp     fm8

fm22:           stc

fm1:            ret

IsThisIt        Endp


;-----------------------------------------------------------------;
;       Write initial Control Record                              ;
;-----------------------------------------------------------------;

WriteInitControl Proc   Near
                Call    WriteTheCtrlRec
                Call    WritePointerRec         ; empty out previous rcds.

                Mov     AX, CurrHandle
                Mov     CtrlHandle, AX
                Mov     AX, OldPID
                Mov     CtrlPID, AX

                Mov     SI, Offset Control_ZM   ; footprint, filelength
                Mov     DI, Offset CtrlBuffer
                Mov     CX, Ctrl_ZM_Size / 2
        Rep     MovSW

                Mov     CtrlDirty, 1
                Call    WriteTheCtrlRec

                Mov     DI, Offset Ctrl_Pointers
                Mov     AX, 0
                Mov     CX, 8
        Rep     StoSW
                Mov     AX, 0FFFFh
                Mov     CX, (PtrsSize / 2) - 8
        Rep     StoSW

                Mov     AX, CurrHandle
                Mov     PtrsHandle, AX
                Mov     AX, OldPID
                Mov     PtrsPID, AX
                Mov     Word Ptr PtrsFilePos, 16
                Mov     Word Ptr PtrsFilePos+2, 0
                Mov     PointersStart, 0
                Mov     PointersEnd,   NumPtrs-1
                Mov     PtrsDirty, 1
                Call    WritePointerRec

                Mov     DX, Offset CtrlBuffer   ; now truncate file length
                Mov     BX, PtrsHandle
                Mov     CX, 0
                CallDOS WriteOp
                Call    CheckWriteError

                Ret
WriteInitControl EndP

;-----------------------------------------------------------------;
;       Read ctrl rec, if present, to determine if file skinny.   ;
;       Return Carry-Clear if it's a skinny file.                 ;
;-----------------------------------------------------------------;

ReadFootPrint   Proc    Near
                Mov     CritFlag, 0

                Mov     AL, 24h
                CallDOS GetVectorOp
                Mov     Int24Ofs, BX
                Mov     Int24Seg, ES

                Push    CS
                Pop     ES

                Mov     AL, 24h
                Mov     DX, Offset ISR24
                CallDOS SetVectorOp

                Call    TooManyCheck
                JC      ReadCtrlFailed

                Mov     BX, CurrHandle
                Mov     AX, 0
                CallDOS IOCTL
                Test    CritFlag, 1
                JNZ     ReadCtrlFailed
                Test    DL, 80h
                JNZ     ReadCtrlFailed

                Mov     BX, CurrHandle          ; file just opened...is
                Mov     CX, 16                  ; already at beginning
                Mov     DX, Offset FootBuffer   ; read just 16 bytes
                CallDOS ReadOp
                JC      ReadCtrlFailed          ; file I/O error.
                Test    CritFlag, 1
                JNZ     ReadCtrlFailed

                Push    CX
                Push    AX

                Mov     AX, 0                   ; position file back at beginning
                Mov     CX, 0
                Mov     DX, CX
                Mov     BX, CurrHandle
                CallDOS SeekOp
                Test    CritFlag, 1
                JNZ     ReadCtrlFailed

                Pop     AX
                Pop     CX

                Cmp     AX, CX
                JNE     ReadCtrlFailed          ; file too short       
                                                ; (no ctrl record)
                Mov     SI, Offset Control_ZM
                Mov     DI, Offset FootBuffer
                Mov     CX, 3
        RepE    CmpSW
                JNE     ReadCtrlFailed          ; footprint not there.

                Jmp     ReadCtrlOkay            ; it's one of ours!

ReadCtrlFailed:
                Mov     AL, 24h
                Mov     DX, Int24Ofs
                Mov     DS, Int24Seg
                CallDOS SetVectorOp
                Push    CS
                Pop     DS
                Mov     CritFlag, 0

                STC
                Ret

ReadCtrlOkay:
                Mov     AL, 24h
                Mov     DX, Int24Ofs
                Mov     DS, Int24Seg
                CallDOS SetVectorOp
                Push    CS
                Pop     DS
                Mov     CritFlag, 0

                CLC
                Ret
ReadFootPrint   EndP


;-----------------------------------------------------------------;
;       Store file handle, etc. for this skinny file              ;
;-----------------------------------------------------------------;

RememberThisFile Proc   Near
                Call    SearchTable
                Mov     BX, TablePtr

                Mov     AX, CurrHandle
                Mov     FileHandleTbl [BX], AX

                Mov     AX, OldPID
                Mov     PIDTbl [BX], AX

                Shl     BX, 1
                Mov     Word Ptr FilePosTbl [BX], 0     ; dbl-word-sized
                Mov     Word Ptr FilePosTbl [BX+2], 0

                Inc     FileCount
                Ret
RememberThisFile EndP

;-----------------------------------------------------------------;
;       Un-Store file handle, etc....file is now closed           ;
;-----------------------------------------------------------------;

ForgetThisFile  Proc    Near
                Mov     BX, TablePtr
                Mov     AX, FileHandleTbl [BX]

                Mov     FileHandleTbl [BX], 0FFFFh      ; mark table
                Mov     PIDTbl [BX], 0FFFFh             ; entries as empty

                Mov     SI, BX
                Mov     DI, DupeTable [SI]
                Cmp     DI, 0FFFFh
                JE      Forget_1

                Mov     DupeTable [SI], 0FFFFh
                Mov     DupeTable [DI], 0FFFFh

Forget_1:       Shl     BX, 1
                Mov     Word Ptr FilePosTbl [BX], 0
                Mov     Word Ptr FilePosTbl [BX+2], 0

Forget_2:       Cmp     AX, CtrlHandle
                JNE     Forget_3
                Mov     CtrlHandle, 0FFFFh
Forget_3:       Cmp     AX, PtrsHandle
                JNE     Forget_4
                Mov     PtrsHandle, 0FFFFh
Forget_4:       Cmp     AX, DeCompHandle
                JNE     Forget_9
                Mov     DeCompHandle, 0FFFFh

Forget_9:       Cmp     FileCount, 0
                JE      ForgetExit

                Dec     FileCount

ForgetExit:     Ret
ForgetThisFile  EndP

;-----------------------------------------------------------------;
;       Find this handle/PID in table (or find 1st free element)  ;
;                                                                 ;
;       If found, return TablePtr = that location and return      ;
;       Carry-Clear.                                              ;
;                                                                 ;
;       If not found, return TablePtr = first free position       ;
;       and Carry-Set.                                            ;
;-----------------------------------------------------------------;

SearchTable     Proc    Near
                Mov     AX, 0FFFFh
                Mov     DI, Offset FileHandleTbl
                Mov     BP, DI
                Mov     CX, MaxHandles
                Push    CX
                Push    DI
        RepNE   ScaSW
                Dec     DI
                Dec     DI
                Sub     DI, BP
                Mov     TablePtr, DI

                Pop     DI
                Pop     CX
                Mov     AX, CurrHandle
        RepNE   ScaSW
                JNE     SearchTable_8

                Dec     DI
                Dec     DI
                Sub     DI, BP
                Mov     AX, OldPID
                Cmp     AX, PIDTbl [DI]
                JNE     SearchTable_8

                Mov     TablePtr, DI
                CLC
                Ret

SearchTable_8:
                STC
                Ret

SearchTable     EndP


;-----------------------------------------------------------------;
;       Save the application PID                                  ;
;-----------------------------------------------------------------;


GetOldPID       Proc    Near
                Xor     AX, AX                  ;to get PSP from DOS
                CallDOS 51h                     ;current PSP now in BX
                Mov     OldPID, BX              ;save it
                Ret
GetOldPID       EndP


;-----------------------------------------------------------------;
;       Tell DOS to use our PID                                   ;
;-----------------------------------------------------------------;

SetOurPID       Proc    Near
                Mov     BX, OurPID              ;set our PSP instead
                Xor     AX, AX
                CallDOS 50h
                Ret
SetOurPID       EndP

;-----------------------------------------------------------------;
;       Tell DOS to resume using the application PID              ;
;-----------------------------------------------------------------;

SetOldPID       Proc    Near
                Mov     BX, OldPID
                Xor     AX, AX
                CallDOS 50h
                Ret
SetOldPID       EndP

;-----------------------------------------------------------------;
;                                                                 ;
;       The actual DECOMPRESS logic                               ;
;       A simple implementation of Lempel-Ziv-Welch               ;
;                                                                 ;
;-----------------------------------------------------------------;

DeCompress      Proc    Near
d1:             call    read_code
                cmp     ax,eof
                jne     d2

d1a:            ret

d2:             cmp     ax,clear
                jne     d7

                mov     nbits,K9
                mov     max_code,K512
                mov     free_code,first_free

                call    read_code

                mov     cur_code,ax
                mov     old_code,ax
                mov     k,al
                mov     fin_char,al
                mov     al,k

                call    write_char
                jmp     d1

d7:             mov     cur_code,ax
                mov     in_code,ax

                cmp     ax,free_code
                jl      d11

                mov     ax,old_code
                mov     cur_code,ax
                mov     al,fin_char

                push    ax
                inc     stack_count

d11:            cmp     cur_code,255
                jle     d15

                mov     bx,cur_code
                mov     al, char [bx]
                push    ax
                inc     stack_count
                shl     bx, 1
                mov     ax, next [bx]
                mov     cur_code,ax

                jmp     d11

d15:            mov     ax,cur_code
                mov     fin_char,al
                mov     k,al

                push    ax
                inc     stack_count
                mov     cx,stack_count

                jcxz    d18

d17:            pop     ax
                call    write_char
                loop    d17

d18:            mov     stack_count,cx
                call    d_add_code

                mov     ax,in_code
                mov     old_code,ax
                mov     bx,free_code
                cmp     bx,max_code
                jl      d23

                cmp     nbits,K10
                je      d23

                inc     nbits
                shl     max_code,1

d23:            jmp     d1

DeCompress      EndP


read_code       proc    near
                mov     ax,bit_offset
                add     ax,nbits
                xchg    bit_offset,ax
                mov     cx,8
                xor     dx,dx
                div     cx

drd0:           add     ax,offset IOBuffer
                mov     si,ax
                lodsw

                mov     bx,ax
                lodsb

                mov     cx,dx
                jcxz    drd2

drd1:           shr     al,1
                rcr     bx,1
                loop    drd1

drd2:           mov     ax,bx
                mov     bx,nbits
                sub     bx,K9
                shl     bx,1
                and     ax,masks[bx]

                ret
read_code       endp



write_char      proc    near
                mov     di,output_offset
                lea     di,DeCompBuffer[di]
                stosb
                inc     output_offset
                ret
write_char      endp


d_add_code      proc    near
                mov     bx,free_code
                mov     al,k
                mov     char [bx],al
                mov     ax,old_code
                shl     bx,1
                mov     next [bx],ax

                inc     free_code
                ret
d_add_code      endp

;-----------------------------------------------------------------;
;                                                                 ;
;       The actual COMPRESS logic                                 ;
;       A simple implementation of Lempel-Ziv-Welch               ;
;                                                                 ;
;-----------------------------------------------------------------;

Compress        Proc    Near
l1:             call    init_table
                mov     ax,clear
                call    write_code

                call    read_char

l4:             xor     ah,ah

l4a:            mov     prefix_code,ax
                call    read_char
                jc      l17

                mov     k,al
                mov     bx,prefix_code
                call    lookup_code
                jnc     l4a

                call    add_code

                push    bx
                mov     ax,prefix_code
                call    write_code
                pop     bx

                mov     al,k
                cmp     bx,max_code
                jl      l4

                cmp     nbits,K10
                jl      l14

                mov     ax,clear
                call    write_code
                call    init_table

                mov     al,k
                jmp     l4

l14:            inc     nbits
                shl     max_code,1
                jmp     l4

l17:            mov     ax,prefix_code
                call    write_code

                mov     ax,eof
                call    write_code

                mov     ax,bit_offset
                cmp     ax,0
                je      l17a

                mov     cx,8
                xor     dx,dx
                div     cx
                or      dx,dx
                je      l17a

                inc     ax

l17a:           mov     CompressLength, ax

                ret

Compress        EndP


init_table      proc    near
                mov     nbits,K9
                mov     max_code,K512

                mov     ax,-1
                mov     cx, K256
                mov     di,offset next
        rep     stosw

                mov     cx, K256
                mov     di,offset first
        rep     stosw

                mov     cx, K256 / 2
                mov     di,offset char
        rep     stosw

                mov     free_code,first_free
                ret
init_table      endp


write_code      proc    near
                push    ax
                mov     ax,bit_offset
                mov     cx,nbits
                add     bit_offset,cx
                mov     cx,8
                xor     dx,dx
                div     cx

                add     ax,offset IOBuffer+6
                mov     di,ax
                pop     ax
                mov     cx,dx
                xor     dx,dx
                jcxz    wc3

wc2:            shl     ax,1
                rcl     dx,1
                loop    wc2

                or      al,byte ptr [di]

wc3:            stosw
                mov     al,dl
                stosb

                ret
write_code      endp


read_char       proc    near
                mov     di,input_offset
                cmp     di,input_size
                jl      rd1

                stc
                ret

rd1:            lea     si,DeCompBuffer[di]
                lodsb
                inc     input_offset

                clc
                ret
read_char       endp


lookup_code     proc    near
                mov     si,bx
                shl     si,1
                mov     di,0
                cmp     first [si],-1
                je      gc4

                inc     di
                mov     bx,first [si]

gc2:            mov     si,bx
                shl     si,1
                cmp     char [bx],al
                jne     gc3

                clc
                mov     ax,bx
                ret

gc3:            cmp     next [si],-1
                je      gc4

                mov     bx,next [si]
                jmp     gc2

gc4:            stc
                ret
lookup_code     endp


add_code        proc    near
                mov     bx,free_code
                cmp     di,0
                je      ac1

                mov     next [si],bx
                jmp     short ac2

ac1:            mov     first [si],bx

ac2:            cmp     bx,maxmax
                je      ac3

                mov     si,bx
                shl     si,1
                mov     first [si],-1
                mov     next [si],-1
                mov     char [bx],al

                inc     free_code

ac3:            ret
add_code        endp

;-----------------------------------------------------------------;
;       Subroutine for doing long division                        ;
;               dividend in DX:AX                                 ;
;               divisor  in BP:BX                                 ;
;               quotient placed in DX:AX                          ;
;-----------------------------------------------------------------;

LongDiv         Proc    Near
                Mov     CL, 1
LDiv1:          Xor     SI, SI
                Mov     DI, BP
                Or      DI, DI
                JNZ     LDiv2
                Div     BX
                XChg    SI, DX
                Jmp     LDiv6
LDiv2:          Push    CX
                Mov     CX, 20
                Mov     DI, SI
LDiv3:          SHL     AX, 1
                RCL     DX, 1
                RCL     SI, 1
                RCL     DI, 1
                Cmp     DI, BP
                JB      LDiv5
                JA      LDiv4
                Cmp     SI, BX
                JB      LDiv5
LDiv4:          Sub     SI, BX
                SBB     DI, BP
                Inc     AX
LDiv5:          Loop    LDiv3

LDiv6:          Test    CL, 2
                JZ      LDiv7
                XChg    AX, SI
                Mov     DX, DI
LDiv7:          Test    CL, 4
                JZ      LDiv8
                Neg     DX
                Neg     AX
                SBB     DX, 0

LDiv8:          Ret
LongDiv         EndP



;-----------------------------------------------------------------;
;       Handle Program Terminations (Int 20h)                     ;
;-----------------------------------------------------------------;

CloseRemaining  Proc    Near

; flush buffers; close any open files

                Call    GetOldPID
                Call    PutBlock
                Call    WritePointerRec
                Call    WriteTheCtrlRec

                Mov     BX, 0
DoISR_4:
                Cmp     FileHandleTbl [BX], 0FFFFh
                JE      DoISR_6
                Mov     AX, OldPID
                Cmp     AX, PIDTbl [BX]
                JNE     DoISR_6

                Push    BX
                Mov     BX, FileHandleTbl [BX]
                CallDOS CloseOP
                Dec     FileCount
                Pop     BX
                Mov     FileHandleTbl [BX], 0FFFFh

DoISR_6:
                Inc     BX
                Inc     BX
                Cmp     BX, MaxHandles * 2
                JB      DoISR_4

DoISR_9:
                Mov     DeCompHandle, 0FFFFh
                Mov     CtrlHandle,   0FFFFh
                Mov     PtrsHandle,   0FFFFh

                Ret
CloseRemaining  EndP


;-----------------------------------------------------------------;
;       Handle Int 24 Critical Errors here                        ;
;-----------------------------------------------------------------;

ISR24   Proc    Far
        Mov     CS:CritFlag, 1
        Mov     AL, 0

        Cmp     CS:DOSVersion, 3
        JB      ISR24Exit

        Mov     AL, 3

ISR24Exit:
        IRet

ISR24   EndP


;-----------------------------------------------------------------;
;       Intercept Int20 (Terminate) call                          ;
;-----------------------------------------------------------------;

ISR_20:
                STI
                Push    DS
                Push    ES

                Push    CS              ; addressability to this segment
                Pop     DS
                Push    DS
                Pop     ES
                CLD

                Call    CloseRemaining

                Pop     ES
                Pop     DS

                Mov     AX, 4C00h
ISR20Exit:      Jmp     CS:OldInt21 




;-----------------------------------------------------------------;
;       Our stack (we don't want to trample someone else's!)      ;
;-----------------------------------------------------------------;

OurStack        DB      256 dup("STACK ")
EndStack        DW      0

;-----------------------------------------------------------------;
;       The following location is the last resident byte          ;
;-----------------------------------------------------------------;
 
EndOfResident   Label   Byte

;-----------------------------------------------------------------;
;                                                                 ;
;       The following is non-resident code/data.  It checks       ;
;       whether Diet Disk is already in memory, and either        ;
;       says "Already loaded!" or it installs the resident        ;
;       portion.                                                  ;
;                                                                 ;
;-----------------------------------------------------------------;

Start:          Push    CS
                Pop     DS
                Call    Installed
                JNC     AlreadyThere
                Jmp     NotPresent              ; nope, it's okay to install

AlreadyThere:   Mov     AH, WriteOp
                Mov     BX, StdOut
                Mov     DX, Offset Msg2
                Mov     CX, Msg2Siz
                Int     21h                     ; "We're already loaded!" message

                Mov     AX, 4C00h               ; exit, we're already loaded.
                Int     21h

;
; change vectors, etc. as necessary to install ourselves
;

NotPresent:     Mov     AX, 5100h               ;to get current PSP from DOS
                Int     21h                     ;PSP now in BX
                Mov     OurPID,bx               ;save our PSP

                Mov     AH, 30h                 ; remember DOS version
                Int     21h
                Mov     DOSVersion, AL
                Mov     DOSVersMin, AH

                Mov     OurSS, DS               ; remember our ss/sp
                Mov     AX, Offset EndStack
                Dec     AX
                Dec     AX
                Shl     AX, 1
                Shr     AX, 1
                Mov     OurSP, AX

                Mov     AH, GetDTAOp            ; get DTA address
                Int     21h
                Mov     OurDTAOfs, BX
                Mov     OurDTASeg, ES

                Mov     AX, 3521h               ; Get address of int 21
                Int     21h
                Mov     Word Ptr OldInt21Ofs, BX
                Mov     Word Ptr OldInt21Seg, ES

                Mov     AX, 3520h               ; Get address of int 20
                Int     21h
                Mov     Word Ptr OldInt20Ofs, BX
                Mov     Word Ptr OldInt20Seg, ES

                Push    DS
                Pop     ES

                Mov     AH, CurrentDiskOp           ; generate <d>:
                Int     21h
                Add     AL, "A"
                Mov     AH, ":"
                Mov     Word Ptr DietPath, AX
                Mov     DietPath+2, '\'

                Mov     SI, Offset DietPath
                Inc     SI
                Inc     SI
                Inc     SI
                Mov     DL, 0
                Mov     AH, GetCurrDir
                Int     21h

                Mov     DI, Offset DietPath
                Mov     CX, MaxName
                Mov     AL, 0
        RepNE   ScaSB
                Dec     DI
                Cmp     Byte Ptr [DI-1], '\'
                JE      DoDietName
                Mov     Byte Ptr [DI], '\'
                Inc     DI

DoDietName:     Mov     SI, Offset DietDir
                Mov     CX, LDietDir
        Rep     MovSB

                Cmp     DOSVersion, 3
                JB      CantShare
                Cmp     DOSVersMin, 1
                JB      CantShare

                Mov     BL, 3
TestNextDrive:
                Mov     AX, 4409h
                Int     21h
                Test    DX, 1000h
                JNZ     YesNetwork
                Inc     BL
                Cmp     BL, 21
                JB      TestNextDrive

                Jmp     Short CantShare

YesNetwork:
                Mov     RD_ONLY, 40h
                Mov     RD_WR,   42h
                Mov     DX, offset DietPath
                Mov     AL, RD_ONLY
                Mov     AH, OpenOp
                Int     21h
                JNC     SaveDietHandle

CantShare:
                Mov     RD_ONLY, 00
                Mov     RD_WR,   02

OpenDietControl:
                Mov     DX, offset DietPath
                Mov     AL, RD_ONLY
                Mov     AH, OpenOp
                Int     21h
                JNC     SaveDietHandle

                Xor     AX,AX                   ; doesn't exist

SaveDietHandle:
                Mov     DietDirHandle, AX
                Cmp     AX, 0
                JE      NoDirFileMode

                Mov     BX, DietDirHandle
                Mov     AH, 3Eh
                Int     21h

                Cmp     RD_ONLY, 0
                JE      StandaloneMode

                Mov     CX, Msg3Siz
                Mov     DX, Offset Msg3
                Jmp     Short StateTheMode

NoDirFileMode:
                Mov     CX, Msg5Siz
                Mov     DX, Offset Msg5
                Jmp     Short StateTheMode

StandaloneMode:
                Mov     CX, Msg4Siz
                Mov     DX, Offset Msg4

StateTheMode:
                Mov     AH, WriteOp
                Mov     BX, StdOut
                Int     21h

                Mov     AH, WriteOp
                Mov     BX, StdOut
                Mov     DX, Offset Msg1
                Mov     CX, Msg1Siz
                Int     21h                     ; "We're loaded" message


;
; now terminate, but stay resident
;
                Mov     DX, offset ISR_21       ; make it point to our routine
                Mov     AX, 2521h
                Int     21h

                Mov     DX, offset ISR_20
                Mov     AX, 2520h
                Int     21h

                Mov     DX, offset EndOfResident
                Mov     CX, 4h
                Shr     DX, CL          ; Turn byte addr. into paragraphs
                Add     DX, 1           ; round up by 1 paragraph
                Mov     AH, 31h
                Mov     AL, 0
                Int     21h             ; terminate/stay resident

; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

Installed       Proc    Near
                Mov     AX, 3341h
                Int     21h
                Cmp     DX, 1234h
                JNE     NotInst

InstAlready:    CLC
                Ret

NotInst:        STC
                Ret
Installed       EndP

;-----------------------------------------------------------------;
;                                                                 ;
;       Non-resident data area                                    ;
;                                                                 ;
;-----------------------------------------------------------------;
Msg1            DB      13,10
                DB      "Diet Disk is loaded. (V 1.0)."
                DB      13,10
                DB      "Distributed from BIX: the BYTE Information Exchange"
                DB      13,10
Msg1Siz         =       $-Msg1

Msg2            DB      13,10
                DB      "Diet Disk is already running."
                DB      13,10
Msg2Siz         =       $-Msg2

Msg3            DB      13,10
                DB      "Diet Disk is in file-sharing mode."
                DB      13,10
Msg3Siz         =       $-Msg3

Msg4            DB      13,10
                DB      "Diet Disk is in non-file-sharing mode."
                DB      13,10
Msg4Siz         =       $-Msg4

Msg5            DB      13,10
                DB      "No DIET.DIR file was found."
                DB      13,10
Msg5Siz         =       $-Msg5

EndOfProgram    =       $

PSP             EndS
                End     Program


