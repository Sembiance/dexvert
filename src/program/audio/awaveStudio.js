import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class awaveStudio extends Program
{
	website    = "https://archive.org/details/awave70_zip";
	bin        = "c:\\Program Files\\Awave Studio\\Awave.exe";
	bruteFlags = { music : {} };
	args       = () => ["-BATCH"];
	loc        = "win2k";
	qemuData   = r => ({
		script : `
			WinWaitActive("Select conversion type", "", 10)
			ControlClick("Select conversion type", "", "[CLASS:Button; TEXT:&Next >]")

			WinWaitActive("Select input files", "", 10)
			ControlClick("Select input files", "", "[CLASS:Button; TEXT:Add...]")

			WinWaitActive("Open new file", "", 10)

			Sleep(250)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			Sleep(250)

			Func ErrorWindows()
				WindowFailure("", "No wave data found!", -1, "{ENTER}")
				WindowFailure("", "Not a Sound Font file", -1, "{ENTER}")
				WindowFailure("Attention!", "You must add at least one", -1, "{ENTER}")
				WindowFailure("Unknown file type!", "", -1, "{ENTER}")
				WindowFailure("", "The file doesn't contain", -1, "{ENTER}")
			EndFunc
			CallUntil("ErrorWindows", ${xu.SECOND*3})

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
	chain = "sox";
	renameOut      = {
		alwaysRename : true,
		regex        : /in - (?:(?:in (?<num>\d+))|(?<name>.+))(?<ext>\.wav)$/,		// either in - NAME.wav  or  in - in - 33.wav
		renamer      :
		[
			({suffix, newName}, {num, ext}) => [newName, " ", num, suffix, ext],
			({suffix}, {name, ext}) => (name && name.length>0 ? [name, suffix, ext] : []),
			({suffix, newName, newExt}) => [newName, suffix, newExt]
		]
	};
}
