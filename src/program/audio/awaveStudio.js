import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class awaveStudio extends Program
{
	website    = "https://archive.org/details/AwaveStudio8.8.zip";
	bin        = "c:\\Program Files\\Awave Studio\\Awave Studio.exe";
	bruteFlags = { music : {} };
	args       = () => ["-BATCH"];
	loc        = "win2k";
	osData     = r => ({
		script : `
			WinWaitActive("Select conversion type", "", 10)
			ControlClick("Select conversion type", "", "[CLASS:Button; TEXT:&Next >]")

			WinWaitActive("Select input files", "", 10)
			ControlClick("Select input files", "", "[CLASS:Button; TEXT:Add files...]")

			$openNewFileWindow = WindowRequire("Open new file", "", 5)
			Sleep(250)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($openNewFileWindow, "", 10)

			Func ErrorWindows()
				WindowFailure("", "No wave data found!", -1, "{ENTER}")
				WindowFailure("", "Invalid float", -1, "{ENTER}")
				WindowFailure("", "Not a Sound Font file", -1, "{ENTER}")
				WindowFailure("Attention!", "You must add at least one", -1, "{ENTER}")
				WindowFailure("Unknown file type!", "", -1, "{ENTER}")
				WindowFailure("", "The file doesn't contain", -1, "{ENTER}")
				return WinActivate("Select input files", "");
			EndFunc
			CallUntil("ErrorWindows", ${xu.SECOND*4})

			$selectInputWindow = WindowRequire("Select input files", "", 10)
			ControlClick($selectInputWindow, "", "[CLASS:Button; TEXT:&Next >]")

			$selectOutputWindow = WindowRequire("Select output options", "", 10)

			$formatWAV = ControlCommand($selectOutputWindow, "", "[CLASS:ComboBox; INSTANCE:2]", "FindString", ".wav - Microsoft Wave file")
			ControlCommand($selectOutputWindow, "", "[CLASS:ComboBox; INSTANCE:2]", "SetCurrentSelection", $formatWAV)
			ControlSetText($selectOutputWindow, "", "[CLASS:Edit; INSTANCE:2]", "c:\\out")
			ControlClick($selectOutputWindow, "", "[CLASS:Button; TEXT:Finish]")

			WaitForPID("Awave.exe", ${xu.MINUTE*5})`
	});
	chain     = "sox";	// no type because I can't guarantee awave will produce a wav file every time
	renameOut = {
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
