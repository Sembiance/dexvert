import {Program} from "../../Program.js";

export class fbm2tga extends Program
{
	website    = "http://fileformats.archiveteam.org/wiki/FBM_image";
	package    = "media-gfx/fbm";
	bin        = "fbm2tga";
	runOptions = async r => ({stdinFilePath : r.inFile({absolute : true}), stdoutFilePath : await r.outFile("out.tga")});
	classify   = true;
	chain      = "dexvert[asFormat:image/tga]";
	renameOut  = true;
}
