import {xu} from "xu";
import {Program} from "../../Program.js";

export class tomsViewer extends Program
{
	website  = "https://tomseditor.com/blog/viewer";
	loc      = "winxp";
	bin      = "c:\\dexvert\\TomsViewer\\TomsViewer.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
		$mainWindow = WindowRequire("Tom's Viewer", "", 5)
		Send("^s")

		$saveAsWindow = WindowRequire("Save As", "", 5)
		Send("c:\\out\\out.png{ENTER}")

		WinWaitClose($saveAsWindow, "", 10)
		WinWaitActive($mainWindow, "", 3)

		Func WaitForOutputFile()
			return FileExists("c:\\out\\out.png")
		EndFunc
		CallUntil("WaitForOutputFile", ${xu.SECOND*5})

		WinClose($mainWindow, "")`
	});

	// if the output file is less than 768 bytes we likely failed to convert properly (multiple tiff files fail this way), just delete it
	verify    = (r, dexFile) => dexFile.size>=768;
	renameOut = true;
}
