import {Program} from "../../Program.js";

export class unpcxgx extends Program
{
	website   = "http://www.ctpax-x.org/?goto=files&show=104";
	loc       = "win2k";
	bin       = "unpcxgx.exe";
	args      = r => [r.inFile()];
	qemuData  = ({cwd : "c:\\out"});
	renameOut = false;
}
