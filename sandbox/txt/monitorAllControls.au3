#include <Array.au3>
#include <WinAPI.au3>

$mainWindow = WindowRequire("Microsoft PhotoDraw", "", 20)

; From: https://www.autoitscript.com/forum/topic/164226-get-all-windows-controls/
Func GetAllWindowsControls($hCallersWindow, $bOnlyVisible=Default, $sStringIncludes=Default, $sClass=Default)
	Local $file = FileOpen("c:\\out.txt", 1)
	If Not IsHWnd($hCallersWindow) Then
		FileWrite($file, "$hCallersWindow must be a handle...provided=[" & $hCallersWindow & "]" & @CRLF)
		FileClose($file)
		Return False
	EndIf
	; Get all list of controls
	If $bOnlyVisible = Default Then $bOnlyVisible = False
	If $sStringIncludes = Default Then $sStringIncludes = ""
	If $sClass = Default Then $sClass = ""
	$sClassList = WinGetClassList($hCallersWindow)

	; Create array
	$aClassList = StringSplit($sClassList, @CRLF, 2)

	; Sort array
	_ArraySort($aClassList)
	_ArrayDelete($aClassList, 0)

	; Loop
	$iCurrentClass = ""
	$iCurrentCount = 1
	$iTotalCounter = 1

	If StringLen($sClass)>0 Then
		For $i = UBound($aClassList)-1 To 0 Step - 1
			If $aClassList[$i]<>$sClass Then
				_ArrayDelete($aClassList,$i)
			EndIf
		Next
	EndIf

	For $i = 0 To UBound($aClassList) - 1
		If $aClassList[$i] = $iCurrentClass Then
			$iCurrentCount += 1
		Else
			$iCurrentClass = $aClassList[$i]
			$iCurrentCount = 1
		EndIf

		$hControl = ControlGetHandle($hCallersWindow, "", "[CLASSNN:" & $iCurrentClass & $iCurrentCount & "]")
		$text = StringRegExpReplace(ControlGetText($hCallersWindow, "", $hControl), "[\\n\\r]", "{@CRLF}")
		$aPos = ControlGetPos($hCallersWindow, "", $hControl)
		$sControlID = _WinAPI_GetDlgCtrlID($hControl)
		$bIsVisible = ControlCommand($hCallersWindow, "", $hControl, "IsVisible")
		If $bOnlyVisible And Not $bIsVisible Then
			$iTotalCounter += 1
			ContinueLoop
		EndIf

		If StringLen($sStringIncludes) > 0 Then
			If Not StringInStr($text, $sStringIncludes) Then
				$iTotalCounter += 1
				ContinueLoop
			EndIf
		EndIf

		If IsArray($aPos) Then
			FileWrite($file, "Func=[GetAllWindowsControls]: ControlCounter=[" & StringFormat("%3s", $iTotalCounter) & "] ControlID=[" & StringFormat("%5s", $sControlID) & "] Handle=[" & StringFormat("%10s", $hControl) & "] ClassNN=[" & StringFormat("%19s", $iCurrentClass & $iCurrentCount) & "] XPos=[" & StringFormat("%4s", $aPos[0]) & "] YPos=[" & StringFormat("%4s", $aPos[1]) & "] Width=[" & StringFormat("%4s", $aPos[2]) & "] Height=[" & StringFormat("%4s", $aPos[3]) & "] IsVisible=[" & $bIsVisible & "] Text=[" & $text & "]." & @CRLF)
		Else
			FileWrite($file, "Func=[GetAllWindowsControls]: ControlCounter=[" & StringFormat("%3s", $iTotalCounter) & "] ControlID=[" & StringFormat("%5s", $sControlID) & "] Handle=[" & StringFormat("%10s", $hControl) & "] ClassNN=[" & StringFormat("%19s", $iCurrentClass & $iCurrentCount) & "] XPos=[winclosed] YPos=[winclosed] Width=[winclosed] Height=[winclosed] Text=[" & $text & "]." & @CRLF)
		EndIf

		If Not WinExists($hCallersWindow) Then ExitLoop
		$iTotalCounter += 1
	Next

	FileWrite($file, @CRLF & @CRLF)
	FileClose($file)
EndFunc

Func MonitorControls()
	GetAllWindowsControls($mainWindow, False)
	Sleep(250)
EndFunc
CallUntil("MonitorControls", ${xu.SECOND*20})
