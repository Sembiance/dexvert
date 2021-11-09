/*
import {Program} from "../../Program.js";

export class qtPicViewer extends Program
{
	website = "https://github.com/Sembiance/dexvert/tree/master/qemu/winxp/data/app/qtw2";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert/tree/master/qemu/winxp/data/app/qtw2",
	unsafe  : true
};

exports.qemu = () => "C:\\WINDOWS\\VIEWER.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	osid        : "winxp",
	inFilePaths : [r.args[0]],
	script      : `
		;Wait for the picture sub window/control to appear

		$mainWinActive = WinWaitActive("[TITLE:Picture Viewer]", "", 10)
		If $mainWinActive Not = 0 Then
			$errorVisible = WinWaitActive("[CLASS:#32770]", "", 1)
			If $errorVisible Not = 0 Then
				Send("{ESCAPE}")
				Sleep(100)
				Send("!f")
				Sleep(200)
				Send("x")
			Else
				WaitForControl("[TITLE:Picture Viewer]", "", "[CLASS:ViewerPictureClass]", ${XU.SECOND*10})
			
				Sleep(500)

				Send("!e")
				Sleep(200)
				Send("c")

				Sleep(250)

				Send("!f")
				Sleep(200)
				Send("x")

				WinWaitClose("[TITLE:Picture Viewer]", "", 10)

				Run('"C:\\WINDOWS\\SYSTEM32\\MSPAINT.EXE"', 'c:\\out', @SW_MAXIMIZE)

				$msPaintWindowVisible = WinWaitActive("[CLASS:MSPaintApp]", "", 10)
				If $msPaintWindowVisible Not = 0 Then
					Send("^v")

					ClipPut("")

					Sleep(250)

					Send("!f")
					Sleep(200)
					Send("a")

					WinWaitActive("[TITLE:Save As]", "", 10)

					Sleep(200)
					Send("c:\\out\\out.png{TAB}p{ENTER}")

					WinWaitClose("[TITLE:Save As]", "", 10)
					Sleep(200)

					Send("!f")
					Sleep(200)
					Send("x")
					Sleep(200)
					Send("n")

					WinWaitClose("[CLASS:MSPaintApp]", "", 10)
				EndIf
			EndIf
		EndIf`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
*/
