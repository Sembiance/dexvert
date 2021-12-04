import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class awaveStudio extends Program
{
	website  = "https://archive.org/details/awave70_zip";
	bin      = "c:\\Program Files\\Awave Studio\\Awave.exe";
	args     = () => ["-BATCH"];
	loc      = "win2k";
	qemuData = r => ({
		script : `
			WinWaitActive("Select conversion type", "", 10)
			ControlClick("Select conversion type", "", "[CLASS:Button; TEXT:&Next >]")

			WinWaitActive("Select input files", "", 10)
			ControlClick("Select input files", "", "[CLASS:Button; TEXT:Add...]")

			WinWaitActive("Open new file", "", 10)

			Sleep(200)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			Sleep(200)

			WinActivate("Select input files", "");
			WinWaitActive("Select input files", "", 10)
			ControlClick("Select input files", "", "[CLASS:Button; TEXT:&Next >]")

			WinWaitActive("Select output options", "", 10)

			Local $formatWAV = ControlCommand("Select output options", "", "[CLASS:ComboBox; INSTANCE:2]", "FindString", ".wav - Microsoft Wave file")
			ControlCommand("Select output options", "", "[CLASS:ComboBox; INSTANCE:2]", "SetCurrentSelection", $formatWAV)

			ControlSetText("Select output options", "", "[CLASS:Edit; INSTANCE:2]", "c:\\out")

			ControlClick("Select output options", "", "[CLASS:Button; TEXT:Finish]")
			
			WaitForPID(ProcessExists("Awave.exe"), ${xu.MINUTE*5})`
	});
	chain = "ffmpeg[outType:mp3]";
}
