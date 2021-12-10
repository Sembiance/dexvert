import {Program} from "../../Program.js";

export class wmf2svg extends Program
{
	website   = "https://github.com/hidekatsu-izuno/wmf2svg";
	package   = "media-gfx/wmf2svg";
	notes     = "This is NOT the wmf2svg provided by libwmf which doesn't work as well";
	bin       = "/opt/bin/wmf2svg";
	args      = async r => [r.inFile(), await r.outFile("out.svg")];
	renameOut = true;
	chain     = "deDynamicSVG";
}
