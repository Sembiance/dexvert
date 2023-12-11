import {xu} from "xu";
import {Program} from "../../Program.js";

export class keyViewPro extends Program
{
	website  = "https://archive.org/details/KeyViewPro/";
	loc      = "win2k";
	flags = {
		outType : "Which type to export to. Default: png"	// technically the KeyView converter allows exporting to a vector based image format too, but that's not currently supported here
	};
	bin      = "c:\\Program Files\\Verity\\KeyView\\kwdd.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$conversionWindow = WindowRequire("KeyView Pro Conversion", "", 10)
			Send("Y")

			Func ErrorOrSuccess()
				WindowFailure("KeyView Pro", "There are no files selected", -1, "{ENTER}")
				return WinActive("KeyView Pro", "Number of files translated")
			EndFunc
			$confirmationWindow =CallUntil("ErrorOrSuccess", ${xu.SECOND*20})

			Send("{ENTER}")
			WinWaitClose($confirmationWindow, "", 10)`
	});
	renameOut  = true;
	chain      = "?dexvert[asFormat:document/rtf]";
	chainCheck = r => r.flags.outType==="pdf";
}
