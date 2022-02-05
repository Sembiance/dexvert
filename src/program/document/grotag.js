import {xu} from "xu";
import {Program} from "../../Program.js";

export class grotag extends Program
{
	website = "http://grotag.sourceforge.net/";
	package = "app-text/grotag";
	flags   = {
		format : "Which output format to generate, pdf or html. Default: pdf (via docbook)"
	};
	bin = "grotag";

	// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
	args    = async r => [r.flags.format==="html" ? "--html" : "--docbook", r.inFile({absolute : true}), await r.outFile("out.xml", {absolute : true})];

	// Grotag can hang at 100% on some guides such as sample bootgauge.guide
	runOptions = ({timeout : xu.MINUTE*1.5});
	chain      = "?dblatex";
	chainCheck = r => r.flags.format!=="html";
	renameOut  = true;
}
