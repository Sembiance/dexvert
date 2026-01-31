import {Program} from "../../Program.js";

export class tkimgConvert extends Program
{
	website    = "http://tkimg.sourceforge.net/";
	package    = "dev-tcltk/tkimg";
	bin        = Program.binPath("tkimgConvert");
	args       = async r => [r.inFile(), await r.outFile("out.png")];
	runOptions = ({virtualX : true});
	renameOut  = true;
}
