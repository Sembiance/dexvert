import {Program} from "../../Program.js";

export class darktable_cli extends Program
{
	website = "https://www.darktable.org/";
	package = "media-gfx/darktable";
	bin     = "darktable-cli";
	args    = async r => [r.inFile(), await r.outFile("out.png")];
}
