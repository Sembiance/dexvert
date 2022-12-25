import {Program} from "../../Program.js";

export class imp extends Program
{
	website   = "https://www.sac.sk/download/pack/imp110d.zip";
	unsafe    = true;
	loc       = "dos";
	bin       = "IMP11/IMP.EXE";
	args      = r => ["e", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({
		preExec : "COPY E:\\DOS\\IMP11\\DOS4GW.EXE E:\\",
		runIn   : "out"
	});
	renameOut = false;
}
