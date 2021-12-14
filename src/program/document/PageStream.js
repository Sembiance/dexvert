import {Program} from "../../Program.js";

export class PageStream extends Program
{
	website  = "https://pagestream.org/";
	loc      = "win2k";
	bin      = "c:\\PageStream\\PageStream5.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("Select Module...", "", 10)
			ControlClick("Select Module...", "", "[CLASS:Button; TEXT:OK]")

			WinWaitActive("Font Substitution", "", 10)
			ControlClick("Font Substitution", "", "[CLASS:Button; TEXT:OK]")

			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("D")
			Sleep(100)

			WinWaitActive("Save As PDF", "", 10)
			ControlClick("Save As PDF", "", "[CLASS:Button; TEXT:Save]")

			Send("c:\\out\\out.pdf{ENTER}")

			WinWaitClose("Save As PDF", "", 10)

			Sleep(200)
			
			Send("^q")`
	});
	renameOut = true;
}
