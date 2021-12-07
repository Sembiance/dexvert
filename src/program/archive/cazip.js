import {Program} from "../../Program.js";

export class cazip extends Program
{
	website   = "https://support.broadcom.com/external/content/release-announcements/CAZIP.exe-CAZIPXP.exe-and-Applyptf/7844";
	loc       = "win2k";
	bin       = "cazip.exe";
	args      = r => ["-u", r.inFile(), "c:\\out\\outfile"];
	renameOut = { name : (r, originalInput) => originalInput.base.trimChars("_") };
}
