************************************************************************
** Sample UserCall Back function for FOXSQZ							   *
** (c) 1993-95 Master Creative Software, Inc.						   *
** Please feel free to use any or all of this code in your app		   *
************************************************************************
* Last Updated 10/20/95 10:30pm WSM


* WARNING FOXSQZ call back routines must follow some rules
*	 1) must always have the same parameter list as defined below
*	 2) Should ALWAYS return back to FOXSQZ !!!
*	 3) must not CANCEL and should not suspend
*	 4) should not take very long to run
*	 5) must not change the current working directory 
*	 6) must never shell out to DOS
*	 7) do not load any other PLB or FLL
*    8) ALWAYS RETURN ZERO in the OTHERWISE Clase of the Case Statement
*       in other words if you do not process a call back message return 0

*#'s 1,2,8 are the most critical rules

** basically all they should do is proccess a message coming from
** FOXSQZ and paint something on the screen.
** Call Back functions were put in to replace FOXSQZ screen output
** and provide a custom output interface which suits your application


Parameters msg,str,i1,i2

*
*   msg = the message that FOXSQZ will pass to your call back funtion
*		 it will also tell your CB function what the parameters passed in are
*   str = for certain messages FOXSQZ will pass a string back . currently it passes
*		 strings back for CBACK_NEW And CBACK_DELETING Messages
*   i1  = these are integers that Foxsqz may pass to the CB function
*   i2    depending on the message
*
*   For those you are interested and don't know this, The method used
*   here is simliar to the way windows programs work (as a veryyy simple example)
*   Windows calls your procedures passing it a message number and parameters.
*   and your procedure would respond to the function. Here FOXSQZ does'nt care what
*   you return , JUST AS LONG AS YOU DO !!
*

** These are the currently supported messages that FOXSQZ sends
** this procedure

#define CBACK_INIT          0	 && When FoxSqz Started
#define CBACK_NEW           1	 && Adding New File to Archive or decompressing
#define CBACK_NEWSTORE      2	 && File will be stored
#define CBACK_UPDATE        3	 && Update Compression progress
#define CBACK_MOV2SQZ       4	 && moving into SQZ file
#define CBACK_RATIO         5	 && return compressed,decompressed size for ratio
#define CBACK_DELETING      6	 && returns the file name that is being deleted from SQZ file
#define CBACK_FMTSTART	    7	 && FOXSQZ sends this when it's about to format a disk
#define CBACK_FORMATING     8	 && Update format
#define CBACK_NXTWR         11   && FOXSQZ is Requesting the Next Disk for Writing
#define CBACK_NXTRD         12   && FOXSQZ is Requesting the Next Disk for Reading
#define CBACK_QUICKFORMAT   14   && FOXSQZ is Quickformating a diskette
#define CBACK_ERASEDISK     15   && FOXSQZ is Erasing All files on a diskette
#define CBACK_FMTDONE       16   && FOXSQZ has completed formating/erasing as diskette

#define NXTDSKCNT       1       && Continue with Next Disk on spanning
#define NXTDSKABT       2       && User abort disk Change  on spanning

* if you return 0 FOXSQZ will respond to the message.


do case
case msg = CBACK_UPDATE
	do slidebar with "",6,i2,i1
case msg = CBACK_INIT
	Wait "Running FOXSQZ ...." Window NoWait
case msg = CBACK_NEW
*	clear
    do slidebar with "I",15,0,0,padr(str,70)
	@4,6 Say Padr("",70)
case msg = CBACK_RATIO
	@4,6 Say str+" -- "+ Ltri(Str(100- (i1/i2*100))) + "% Compressed"
case  msg = CBACK_MOV2SQZ
	@4,6 Say "Copying ["+str+"] into archive"
case msg = CBACK_DELETING
	@4,5 Say "Deleteing "+str
case msg = CBACK_FMTSTART
	do slidebar with "I",15,0,0,"Please Wait , Formating Drive "+str+":"
case msg = CBACK_FORMATING
    do slidebar with "",15,i2,i1
case msg = CBACK_QUICKFORMAT
    Wait 'Quick Formating Drive '+str  Window NoWait
case msg = CBACK_ERASEDISK
    Wait 'Erasing Contents of Drive '+str  Window NoWait  
case msg = CBACK_FMTDONE
    Wait 'Diskette preparation completed' Window Timeout .5
    Wait clear
case (msg = CBACK_NXTWR OR msg = CBACK_NXTWR)
    Wait "Put Next Disk In,Strike Any Key - ESC to Abort " Window To x
    if lastKey() = 27
        Return NXTDSKABT     
    Else    
        return NXTDSKCNT    
    Endif
EndCase

** for Call Backs that require a return Value Back to FOXSQZ
** Return 0 and FOXSQZ will use default processing

Return 0 




*************************************************************************
Procedure SlideBar
************************************************************************
Parameters _Smsg,_Srow,_i1,_i2,_Msg

** SLIDE BAR UDF v1.00 By Warren Master Nov 1991

**USSAGE:
*************************************************************
*_Smsg Set To "I" for First Time and Nothing After That    *
*_Srow Row Where Bar Will Move                              *
*_i1 Number of Thing We Want to do                       *
*_i2 The Number of Things We have Done So far          *
*************************************************************

**********************************************************
*Example                                                 *
**********************************************************
* TOTRECS=reccount()
* CCNT=0
* go top
* do slidebar with "I",20,TOTRECS,CCNT
* Do While
*     Do something
*     Skip
*    CCNT=CCNT+1
*    do slidebar with "",20,TOTRECS,CCNT
*
* Enddo

if upper(_smsg)=="I"
	if !WExist('Thermo')
		define Window Thermo From _srow-3,2 TO _srow+3,78 Double Color GR+/BG
		Activate Window Thermo
	Endif
	@ 0,0 say _msg
	@ 1,5 say "旼컴컴컴컴컴컴컴컴쩡컴컴컴컴컴컴컴쩡컴컴컴컴컴컴컴컫컴컴컴컴컴컴컴컴커"
	@ 2,5 say "�0%              25%             50%              75%            100%�"
	@ 3,5 say "읕컴컴컴컴컴컴컴컴좔컴컴컴컴컴컴컴좔컴컴컴컴컴컴컴컨컴컴컴컴컴컴컴컴켸"
else
	@ 2,6 fill to 2,6+round(66*(_i2/_i1)+.50,0) color n/w,w/n
endif

return
