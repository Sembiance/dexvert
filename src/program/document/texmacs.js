import {Program} from "../../Program.js";

export class texmacs extends Program
{
	website    = "https://www.texmacs.org/";
	package    = "app-office/texmacs";
	bin        = "texmacs";
	runOptions = ({virtualX : true});
	args       = async r => ["-c", r.inFile(), await r.outFile("out.pdf"), "-q"];
	renameOut  = true;
}
