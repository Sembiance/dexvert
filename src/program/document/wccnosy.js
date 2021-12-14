import {Program} from "../../Program.js";

export class wccnosy extends Program
{
	website       = "http://www.dreamlandbbs.com/filegate/wcf/4utl/index.html";
	loc           = "dos";
	bin           = "WCCNOSY.EXE";
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	args          = r => [" /indent=2", r.inFile()];
	dosData       = () => ({runIn : "out"});
	renameOut     = true;
}
