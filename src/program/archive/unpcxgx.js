import {Program} from "../../Program.js";

export class unpcxgx extends Program
{
	website   = "http://www.ctpax-x.org/?goto=files&show=104";
	loc       = "win7";
	bin       = "unpcxgx.exe";
	args      = r => [r.inFile()];
	osData    = ({cwd : "c:\\out"});
	renameOut = false;
}
