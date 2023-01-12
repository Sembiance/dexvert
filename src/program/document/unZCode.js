import {Program} from "../../Program.js";

export class unZCode extends Program
{
	website    = "https://www.inform-fiction.org/zmachine/ztools.html";
	package    = "games-util/ztools";
	bin        = "deno";
	args       = async r => Program.denoArgs(Program.binPath("unZCode.js"), "--", r.inFile(), await r.outFile("out.txt"));
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
}
