import {Program} from "../../Program.js";

export class slim extends Program
{
	website       = "https://archive.org/details/msdos_shareware_fb_SLIM110A";
	loc           = "dos";
	bin           = "SLIM110A/SLIM.EXE";
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = r => ({autoExec : [`..\\dos\\SLIM110A\\SLIM.EXE on`, `..\\dos\\SLIM110A\\SLIM.EXE X ${r.inFile({backslash : true})}`], runIn : "out"});
	renameOut     = false;
}
