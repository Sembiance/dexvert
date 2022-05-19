Local $goFilePath = "c:\in\go.au3"

Func waitForGo()
	While Not FileExists($goFilePath)
		Sleep(100)
	WEnd

	While FileGetSize($goFilePath) = 0
		Sleep(100)
	WEnd

	Sleep(100)
EndFunc

Sleep(2000)

InetGet("http://192.168.50.2:17735/qemuReady?osid=win2k&ip=" & @IPAddress1, "c:\dexvert\qemuReadyResult.txt")

While 1
	waitForGo()

	RunWait("c:\Program Files\AutoIt3\AutoIt3.exe" & " " & $goFilePath, "")
	Sleep(100)
	FileDelete($goFilePath)
WEnd
