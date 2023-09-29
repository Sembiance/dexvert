import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class fileMerlin extends Program
{
	website = "http://www.file-convert.com/flmn.htm";
	unsafe  = true;
	flags   = {
		// For a list of valid SRC and DEST format names, see programs_formats.txt
		type    : "Which format to specify for the input format. Default: AUTO (let FileMerlin decide)",
		outType : "Which format to specify for the output. Default: PDF"
	};
	loc       = "winxp";
	bin       = "c:\\ACI Programs\\FMerlin\\fmn.exe";
	args      = r => [`in(${path.basename(r.inFile())})`, `sfrm(${r.flags.type || "AUTO"})`, "out(c:\\out\\*.pdf)", `dfrm(${r.flags.outType || "PDF"})`];
	osData    = ({
		timeout  : xu.MINUTE,
		alsoKill : ["drwtsn32.exe"],
		script   : `
			; Wait 5 seconds for it to handle the file on it's own and Exit if the process finished
			If Not WaitForPID("fmn.exe", ${xu.SECOND*5}) Then Exit 0

			; Otherwise we may have a warning we need to dismiss
			Func DismissWarnings()
				WinClose("FileMerlin/Pdf (15-user) -- needs network setup")
			EndFunc
			CallUntil("DismissWarnings", ${xu.SECOND*5})

			WaitForPID("fmn.exe", ${xu.SECOND*10})`});
	verify    = (r, dexFile) => !dexFile.dir.endsWith("_g");
	renameOut = true;
}
