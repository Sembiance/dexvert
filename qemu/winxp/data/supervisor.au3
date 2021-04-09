Local $goFilePath = "c:\in\go.au3"

Func waitForGo()
	While Not FileExists($goFilePath)
		Sleep(100)
	WEnd
EndFunc

InetGet("http://192.168.51.2:17735/qemuReady?osid=winxp&ip=" & @IPAddress1, "c:\dexvert\qemuReadyResult.txt")

While 1
	waitForGo()

	RunWait("c:\Program Files\AutoIt3\AutoIt3.exe" & " " & $goFilePath, "")
	Sleep(100)
	FileDelete($goFilePath)
WEnd
