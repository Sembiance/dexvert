import {Program} from "../../Program.js";

export class acm2wav extends Program
{
	website   = "http://return0.pisem.net/audio.html";
	loc       = "win7";
	bin       = "acm2wav.exe";
	args      = r => [r.inFile()];
	osData    = ({cwd : "c:\\out"});
	renameOut = true;
	chain     = "sox[type:wav]";
}
