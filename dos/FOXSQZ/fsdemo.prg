************************************************************************
** Demo program for Foxsqz.PLB/.FLL									   *
** (c) 1993-94 Master Creative Software, Inc.						   *
** Please feel free to use any or all of this code in your app		   *
************************************************************************
* Last Updated 10/21/94 10:45pm WSM


Set echo off
Set talk off
Set Escape Off
Clear all
Close all
Clear
set textmerge  show

On Key Label Alt-Z Suspe

_ExitBtn  =   0													&& Button status
SqzCallBck=  .T.												&& Use FOXSQZ Call BAck Function
SqzStrict =  .F.												&& Enable Strict Mode
SqzPage   =  .T.												&& Page Listing
SqzArc    =  Padr("FOXSQZ.SQZ",30," ")							&& Archive File Name
SqzPass   =  Space(20)											&& Password for Encryption
SqzFSpec  =  PADR("*.*",30)										&& Files to Act on
SqzXClude =  Space(25)											&& Files to Exclude
SqzINCFile=  Space(25)											&& Include File Name

SqzCmpTyp =  2													&& Compression Method
SqzOver   =  .F.												&& OverWrite Existing files when decompressing
SqzDst    =  Space(25)											&& destination for Decompression
SqzRestDT =  .F.												&& restore Orginal Date time of File
SqzQuiet  =  .F.												&& Operate quietly
SqzSpan   =  .F.												&& Span Disks
SqzWipe   =  .F.												&& Wipe disk used for spanning
SqzFmtTyp =   1													&& Format MEthod
SqzLowDens=  .F.												&& LowDensity Disks Used
SqzVerify =  .F.												&& DOS Verfy Flag
SqzTDrv   =  "  "												&& Temp Drive
SqzIncSub =  .F.												&& Include Subdirectories
SqzStoPath=  .F.												&& Store PathNames
SqzResTree=  .F.												&& Restore Directory Tree
SqzStorSpec= .F.												
SqzLowMem  = .F.												&& Use Min Memory Allocations
SqzInq     = 1													&& Which Inquiry Function To Run

* Intialize Error Strings Foxsqz returnes offset-1 into this array
* so you need to add one when indexing the array, this is because
* foxpro arrays start at offset 1 and Foxsqz returns 0 for success..

Dime FoxSqzErr[52]

FoxSqzErr[1] = "No Errors Were Detected"
FoxSqzErr[2] = "Invalid or Bad Input File "
FoxSqzErr[3] = "Invalid or Bad Output File"
FoxSqzErr[4] = "Invalid or Bad Global Header in SQZ file"
FoxSqzErr[5] = "Error Writing Global Header"
FoxSqzErr[6] = "Invalid or Bad Local Header"
FoxSqzErr[7] = "Error Writing Local Header"
FoxSqzErr[8] = "Error allocating Local Memory"
FoxSqzErr[9] = "Error Allocating Foxpro memory"
FoxSqzErr[10] = "File Read Error Type 1"
FoxSqzErr[11] = "File Read Error Type 2"
FoxSqzErr[12] = "File Read Error Type 3"
FoxSqzErr[13] = "DosFile Size Error"
FoxSqzErr[14] = "File Write Error Type 1"
FoxSqzErr[15] = "File Write Error Type 2"
FoxSqzErr[16] = "File Write Error Type 3"
FoxSqzErr[17] = "Error In Parameter 1 (Options String)"
FoxSqzErr[18] = "Error In Parameter 2 (SQZ file Name)"
FoxSqzErr[19] = "Error In Parameter 3 (File Specifiers)"
FoxSqzErr[20] = "Error Opening Input"
FoxSqzErr[21] = "Error Opening OutPut"
FoxSqzErr[22] = "No Parameters Passed "
FoxSqzErr[23] = "Error Opening WorkFile"
FoxSqzErr[24] = "File Write Error"
FoxSqzErr[25] = "Create Aborted By User"
FoxSqzErr[26] = "Error Allocating Transfer Memory"
FoxSqzErr[27] = "Error InValid/Unknown Parameter"
FoxSqzErr[28] = "UnKnown compression type"
FoxSqzErr[29] = "Error in Password"
FoxSqzErr[30] = "InValid PassWord"
FoxSqzErr[31] = "Not a FOXSQZ Archive or Incompatible version"
FoxSqzErr[32] = "Error in specified destination drv/path"
FoxSqzErr[33] = "Unable to select target	drive/path"
FoxSqzErr[34] = "Could not Open Include File"
FoxSqzErr[35] = "Invalid Inclusion argument"
FoxSqzErr[36] = "Invalid Exclusion argument"
FoxSqzErr[37] = "Max Exclusions is 5"
FoxSqzErr[38] = "I needed disk #1 to Start"
FoxSqzErr[39] = "User aborted"
FoxSqzErr[40] = "No Spanning support for this function"
FoxSqzErr[41] = "Unable to Format Disk"
FoxSqzErr[42] = "Nothing to do "
FoxSqzErr[43] = "Exceeded max files allowed in demo"
FoxSqzErr[44] = "Disk is Not Removable, will not format"
FoxSqzErr[45] =  "No More Internal FoxSqz Memory Handles"
FoxSqzErr[46] =  "Invalid Drive"
FoxSqzErr[47] =  "Unable to Open Source File In Strict Mode"
FoxSqzErr[48] =  "MEMO field not supported for requested function"
FoxSqzErr[49] =  "DOS Crtical Error detected via int24"
FoxSqzErr[50] =  "Invalid Call Back Function"
FoxSqzErr[51] =  "Insufficient disk space"


Done = .F.
Clear
Do While !Done
	Clear
	Text                                                                          


          ллллллл     ллл     лл   лл    лллл      лллл     ллллллл          
           лл   л    лл лл    лл   лл   лл  лл    лл  лл    лл   лл          
           лл л     лл   лл    лл лл    ллл       лл  лл    л   лл           
           лллл     лл   лл     ллл      ллл      лл  лл       лл            
           лл л     лл   лл     ллл        ллл    лл ллл      лл  л          
           лл        лл лл     лл лл    лл  лл     лллл      лл  лл          
          лллл        ллл     лл   лл    лллл        ллл    ллллллл          


             FOXSQZ (c) 1991-1995 Master Creative Software, Inc.
                              All Rights Reserved

                          Release 1.8e October 12, 1995

              Support: BBS (201) 585-7002, COMPUSERVE: 70713,2002
              
              Please see the About FOXSQZ dialog and take time to
              review the FOXSQZ ehlp file, both available from the
              main menu.
              
	EndText
	do foxsqz.mpx	
	activate menu _MSYSMENU

Enddo

Clear all
Clear

Set SysMenu To Defa




****************************************************************************
Procedure ExeFoxSqz
******************************************************************************

* Foxsqz dispatcher pass in either S,U,L,D,I 
* variables filled in by screen modules which call this function
* FSCOMP,FSDCOMP,FSINQ,FSLIST

Parameter Fnct

** Build FoxSqz Argument string ***

SRet = 0
Arg1 = Fnct

if Fnct = "I"													&& InQuiry

	Arg1 = Arg1 + "("
	** This code is here to make sure the Inquiry function Modifer is not split off
	** from the I parameter.

	Do Case
	Case SqzInq = 1  &&  Squezzed File Size
		Arg1 = Arg1 + "S"
	Case SqzInq = 2  &&  Un-Squezzed File Size
		Arg1 = Arg1 + "U"
	Case SqzInq = 3 && Squezzed File Count
		Arg1 = Arg1 + "C"
	Case SqzInq = 4	 &&  Load Array with File Info
		Arg1 = Arg1 + "A"
	EndCase

	Arg1 = Arg1 + ")"

Endif



*Now Create Arguments that affect all Foxsqz Function

if !Empty(SqzPass)												&& Is Password Encryption Requested ?
	Arg1 = Arg1 + "E("+allTrim(SqzPass)+")"
Endif

if SqzQuiet
	Arg1 = Arg1 + "Q"
Endif

if SqzStrict
	Arg1 = Arg1 + "0"
Endif

if SqzLowMem
	Arg1 = Arg1 + "$"
Endif

if SqzVerify													&& Need Dos Verify Flag Set ?
	Arg1 = Arg1 + "V"
Endif

if !Empty(SqzTDrv)												&& Want to Redirect Foxsqz Tmp Files ?
	Arg1 = Arg1 + "G("+Trim(SqzTDrv)+")"
Endif

if !Empty(SqzXClude)											&& Was there any files to Exclude
	Ex1 = ""
	l = len(Trim(SqzXClude))
	for i = 1 to l
		tmp = Substr(SqzXClude,i,1)
		if tmp = " "
			if !Empty(Ex1)
				Arg1 = Arg1 + "X("+Ex1+")"
				Ex1 = ""
			else
				*ignore leading trailing space
			Endif
		else
			Ex1 = Ex1 + tmp
		Endif
	EndFor
	if !Empty(Ex1)												&& Get Last Arg
		Arg1 = Arg1 + "X("+Ex1+")"
	Endif
Endif

* Now Proccess Squeeze Modifiers

if Fnct = "S"													&& Compression Modifiers

	** compression Type Fast Maximum or None
	Arg1 = Arg1 + iif(SqzCmpTyp=1,"M",iif(SqzCmpTyp=2,"F","N"))

	** Use a Include File ?
	if !Empty(SqzINCFile)
		Arg1 = Arg1 + "@("+allTrim(SqzINCFile)+")"
	Endif

	** Recurse into Subdirectories ?
	if SqzIncSub
		Arg1 = Arg1 + "R"
	Endif

	**Store Paths Recursed Into ?
	if SqzIncSub AND SqzStoPath
		Arg1 = Arg1 + "P"

		** What about paths specified
		if SqzStorSpec
			Arg1 = Arg1 + "*"
		Endif
	Endif

	** Span Multiple Floppies
	if SqzSpan
		Arg1 = Arg1 + "&"
	Endif

	** Format the Target if Removable ?
	if SqzWipe
		Arg1 = Arg1 + "W("

		** How do we eant to Format it QUICK , Conditionaly or Unconditionaly
		do case
		case SqzFmtTyp = 1
			Arg1 = Arg1 + "q"
		case SqzFmtTyp = 2
			Arg1 = Arg1 + "c"
		case SqzFmtTyp = 3
            Arg1 = Arg1 + "u"
		case SqzFmtTyp = 4
			Arg1 = Arg1 + "e"

		EndCase
		** format Low Density disks ?
		if SqzLowDens
			Arg1 = Arg1 + "l"
		Endif

		** Close Wipe Modifiers
		Arg1 = Arg1 + ")"
	Endif

Endif

** Process UnSqueeze Function

if Fnct="U"

	* Overwrite Existing Files ?
	if SqzOver
		Arg1 = Arg1 + "O"
	Endif

	** Restore Original File Date and Time ?
	if SqzRestDT
		Arg1 = Arg1 + "R"
	Endif

	** Restore to Driver/Directory other than Default ?
	if !Empty(SqzDst)
		if Right(AllTrim(SqzDst),1)!="\"
			SqzDst = Padr(AllTrim(SqzDst)+"\",15," ")
		Endif
		Arg1 = Arg1 + "T("+allTrim(SqzDst)+")"
	Endif

	** Restore Directory Tree ?
	if SqzResTree
		Arg1 = Arg1 + "P"
	Endif

Endif

** Proccess List Option
if Fnct="L" AND SqzPage											&& Page the Display "More Like"
	Arg1 = Arg1 + "P"
Endif



if SqzCallBck
	Arg1 = Arg1 + "!(SAMPCB)"
Endif



* Make FOXSQZ part of Foxpro

If "2.0" $VERSION()
	Wait "Foxpro 2.0 PLB not Included" Window
Else
	Set libr TO FOXSQZ											&& FOXPRO 2.5 - 2.6 users
Endif

SqzRunStr  = ' =FoxSqz("'+ Arg1 + '","'+allTrim(SqzArc) +'","' + allTrim(SqzFSpec)+'")'
Show Gets

if Empty(SqzFSpec)
	SRet = FoxSqz(Arg1,allTrim(SqzArc))
Else
	SRet = FoxSqz(Arg1,allTrim(SqzArc),allTrim(SqzFSpec))
Endif

if SRet=0 AND Fnct = "L"
	Wait "Strike Any Key " Window
Endif

Set Libr to
Wait Clear

if SqzCallBck
	Release Window Thermo
Else
	Release Window SQZ	
Endif

Clear TypeAhead

SqzRetStr = "["+Ltrim(Str(SRet))+"] - "+SqzError(SRet) 
Show Gets
Return Sret

*******************************************
Procedure SqzError
*******************************************
Param _Er

if _Er >=0
	return FoxSqzErr[_er+1]
Else
	Return "Inquiry Results Returned"
Endif
