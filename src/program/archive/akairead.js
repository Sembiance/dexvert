import {xu} from "xu";
import {Program} from "../../Program.js";

export class akairead extends Program
{
	website    = "https://www.lsnl.jp/~ohsaki/software/akaitools/";
	package    = "app-arch/akaitools";
	bin        = "akairead";
	args       = r => ["-f", r.inFile(), "-d", r.outDir(), "-R", "/"];
	renameOut  = false;
}
