import {Program} from "../../Program.js";

export class bdftopcf extends Program
{
	website   = "https://gitlab.freedesktop.org/xorg/app/bdftopcf";
	package   = "x11-apps/bdftopcf";
	bin       = "bdftopcf";
	args      = async r => ["-o", await r.outFile("out.pcf"), r.inFile()];
	renameOut = true;
	chain     = "dexvert[asFormat:font/pcf]";
}
