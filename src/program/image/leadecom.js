import {Program} from "../../Program.js";

export class leadecom extends Program
{
	website   = "https://archive.org/details/JPEG35_ZIP";
	unsafe    = true;
	loc       = "dos";
	bin       = "LEADTOOL/LEADECOM.EXE";
	args      = async r => [r.inFile(), await r.outFile("OUT.TGA", {backslash : true}), "/TGA24"];
	renameOut = true;
	chain     = "dexvert[asFormat:image/tga]";
}
