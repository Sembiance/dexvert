import {Program} from "../../Program.js";

export class sdoTool extends Program
{
	website   = "https://github.com/xiphoseer/sdo-tool";
	package   = "app-text/sdo-tool";
	bin       = "sdo-tool";
	args      = async r => ["--format", "html", r.inFile(), await r.outFile("out.html")];
	renameOut = true;
	notes     = "This could be improve to output actual character glyphs in a PDF, see https://github.com/Sembiance/dexvert/issues/28";
}
