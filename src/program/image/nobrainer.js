import {Program} from "../../Program.js";

export class nobrainer extends Program
{
	website   = "http://asylum.acornarcade.com/a_nobrainer.php";
	package   = "media-gfx/nobrainer";
	bin       = "nobrainer";
	args      = async r => ["-f", "-s", r.inFile(), await r.outFile("outfile")];
	renameOut = false;
	chain     = "dexvert[asFormat:image/acornSprite]";
}
