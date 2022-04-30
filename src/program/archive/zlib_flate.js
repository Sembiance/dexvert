import {xu} from "xu";
import {Program} from "../../Program.js";

export class zlib_flate extends Program
{
	website    = "https://qpdf.sourceforge.net/";
	package    = "app-text/qpdf";
	bin        = "zlib-flate";
	args       = () => ["-uncompress"];
	runOptions = async r => ({stdinFilePath : r.inFile({absolute : true}), stdoutFilePath : await r.outFile("out"), timeout : xu.MINUTE*2, killChildren : true});
	renameOut  = true;
}
