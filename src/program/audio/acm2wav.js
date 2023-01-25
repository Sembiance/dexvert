import {Program} from "../../Program.js";

export class acm2wav extends Program
{
	website   = "http://return0.pisem.net/audio.html";
	loc       = "win2k";
	bin       = "acm2wav.exe";
	args      = r => [r.inFile()];
	qemuData  = ({cwd : "c:\\out"});
	renameOut = true;
	chain     = "sox";
}
