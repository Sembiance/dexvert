import {Program} from "../../Program.js";

export class yydecode extends Program
{
	website   = "http://yydecode.sourceforge.net/";
	package   = "net-news/yydecode";
	bin       = "yydecode";
	args      = r => ["-D", r.outDir(), r.inFile()];
	renameOut = false;
}
