import {Program} from "../../Program.js";

export class x2tga extends Program
{
	website    = "https://paulbourke.net/dataformats/avs_x/xtoraw.c";
	package    = "media-gfx/x2tga";
	bin        = "x2tga";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.tga")});
	classify   = true;
	chain      = "convert[format:tga][flip]";
	renameOut  = true;
}
