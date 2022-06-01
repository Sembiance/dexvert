import {Program} from "../../Program.js";
import {path} from "std";

export class MDFtoISO extends Program
{
	website  = "http://www.mdftoiso.com/";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\Program Files\\MDF to ISO\\mdftoiso.exe";
	args     = () => [];
	qemuData = r => ({
		alsoKill : ["mdf2iso.exe"],	// MDFtoISO uses MDF2ISO behind the scenes
		script : `
			WinWaitActive("MDF to ISO", "", 10)

			ControlSetText("MDF to ISO", "", "[CLASS:TEdit; INSTANCE:2]", "c:\\in\\${path.basename(r.inFile())}")
			ControlSetText("MDF to ISO", "", "[CLASS:TEdit; INSTANCE:1]", "c:\\out\\out.iso")

			Sleep(1000)

			ControlClick("MDF to ISO", "", "[CLASS:TButton; TEXT:Convert]")

			WindowFailure("Error", "", 5, "{ENTER}")

			Local $isComplete = WinWaitActive("Information", "", 30)
			If $isComplete Then
				ControlClick("Information", "", "[CLASS:TButton; TEXT:OK]")
			EndIf

			WinWaitActive("MDF to ISO", "", 10)
			ControlClick("MDF to ISO", "", "[CLASS:TButton; TEXT:Close]")

			WinWaitClose("MDF to ISO", "", 10)

			ProcessWaitClose("mdftoiso.exe", 10)`
	});
	renameOut = false;
	chain     = "dexvert";
}
