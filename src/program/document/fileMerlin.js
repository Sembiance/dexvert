import {xu} from "xu";
import {Program} from "../../Program.js";

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
	args      = r => [`in(${r.inFile()})`, `sfrm(${r.flags.type || "AUTO"})`, "out(c:\\out\\*.pdf)", `dfrm(${r.flags.outType || "PDF"})`];
	qemuData  = ({
		timeout : xu.MINUTE,
		script : `
			WaitForPID(ProcessExists("fmn.exe"), ${xu.SECOND*30});
			$errorVisible = WinWaitActive("FileMerlin/Pdf (15-user) -- needs network setup", "", 7)
			If $errorVisible Not = 0 Then
				WinClose("FileMerlin/Pdf (15-user) -- needs network setup");
			EndIf
			WaitForPID(ProcessExists("fmn.exe"), ${xu.SECOND*30});
			ProcessClose("fmn.exe")
			WaitForPID(ProcessExists("fmn.exe"), ${xu.SECOND*5});`});
	verify    = (r, dexFile) => !dexFile.dir.endsWith("_g");
	renameOut = true;
}
