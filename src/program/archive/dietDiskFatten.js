import {Program} from "../../Program.js";

export class dietDiskFatten extends Program
{
	website       = "http://cd.textfiles.com/nightowl/nopv06/010A/DIETDISC.ZIP";
	loc           = "dos";
	bin           = "DIETDISK/FATTEN.EXE";
	args          = r => [r.inFile({backslash : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({
		preExec : "..\\dos\\DIETDISK\\DIETDISK.COM",
		runIn   : "out"
	});
	renameOut     = true;
}
