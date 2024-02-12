import {xu} from "xu";
import {Program} from "../../Program.js";

export class pco extends Program
{
	website   = "https://vetusware.com/download/PC%20Outline%20for%20Windows%20PC%20Outline%201.0.a/?id=4597";
	unsafe    = true;
	loc       = "dos";
	bin       = "PCO/PCO.EXE";
	dosData   = r => ({
		timeout  : xu.MINUTE*3,
		autoExec : [`COPY ${r.inFile({backslash : true}).toUpperCase()} DOS\\PCO\\F.PCO`, "CD DOS\\PCO", "PCO.EXE"],
		keys     : [" ", " ", ["Down"], ["Enter"], ["Enter"], {delay : xu.SECOND*5}, ["Insert"], ["Right"], ["Right"], ["Right"], ["Right"], "d", "a", "g", `E:\\${r.f.outDir.base}\\OUTFILE.TXT`, ["Enter"], ["Escape"], ["Escape"], "y"]
	});
	renameOut = true;
}
