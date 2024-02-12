import {Program} from "../../Program.js";

export class rol2mus extends Program
{
	website   = "https://vgmpf.com/Wiki/index.php?title=AdLib_Convert";
	loc       = "dos";
	bin       = "ROL2MUS/CONVERT.EXE";
	args      = r => [`..\\..\\${r.inFile()}`, "DEXVERT.SND", `..\\..\\${r.f.outDir.base}\\DEXVERT.MUS`];
	dosData   = r => ({runIn : "prog", autoExec : ["COPY ..\\..\\*.INS .", "COPY ..\\..\\INS\\*.* .", `CONVERT.EXE ${r.dosData.args.join(" ")}`]});
	renameOut = true;
	chain     = "adplay";
}
