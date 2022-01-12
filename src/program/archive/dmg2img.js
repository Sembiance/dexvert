import {Program} from "../../Program.js";

export class dmg2img extends Program
{
	website = "http://vu1tur.eu.org/tools";
	package = "sys-fs/dmg2img";
	unsafe  = true;
	bin     = "dmg2img";
	args    = async r => [r.inFile(), await r.outFile("out.img")];

	// Convert with dexvert any resulting files
	chain = "dexvert";
	renameOut = true;
}
