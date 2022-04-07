import {Program} from "../../Program.js";

export class txd extends Program
{
	website    = "https://www.inform-fiction.org/zmachine/ztools.html";
	package    = "games-util/ztools";
	bin        = "txd";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}
