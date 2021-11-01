"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://web.archive.org/web/20060210083422/http://snoopy81.ifrance.com/snoopy81/en/winpack.htm",
	unsafe  : true
};

exports.qemu = () => "c:\\dexvert\\WinPack300b\\WinPack.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.args[0]],
	dontMaximize : true,
	script       : `
		$mainWindowVisible = WinWaitActive("[TITLE:WinPack; CLASS:TisMainForm]", "", 10)
		If $mainWindowVisible = 0 Then
			Local $errorVisible = WinWaitActive("Erreur", "", 5)
			If $errorVisible Not = 0 Then
				ControlClick("Erreur", "", "[TEXT:OK]")
			Else
				Local $errorTwoVisible = WinWaitActive("Avertissement", "", 5)
				If $errorTwoVisible Not = 0 Then
					ControlClick("Avertissement", "", "[TEXT:OK]")
				EndIf
			EndIf
		Else
			Sleep(1000)

			Send("!f")
			Sleep(200)
			Send("u")

			WinWaitActive("[TITLE:Browse for Folder]", "", 10)

			Sleep(1000)

			Send("{DOWN}")
			Sleep(100)
			Send("{RIGHT}")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{ENTER}")

			WinWaitClose("[TITLE:Browse for Folder]", "", 10)

			Sleep(1000)

			Send("!f")
			Sleep(200)
			Send("x")
		EndIf

		WaitForPID(ProcessExists("WinPack.exe"), ${XU.SECOND*10})`
});
