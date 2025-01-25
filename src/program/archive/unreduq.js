import {Program} from "../../Program.js";

export class unreduq extends Program
{
	website       = "https://dev.discmaster2.textfiles.com/browse/22795/PCA110_09_02.ISO/mag/reduq/reduq.exe";
	loc           = "dos";
	bin           = "UNREDUQ.EXE";
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	args          = r => [r.inFile({backslash : true})];
	dosData       = () => ({runIn : "out"});
	renameOut     = false;
}
