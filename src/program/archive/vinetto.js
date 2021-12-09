import {Program} from "../../Program.js";

export class vinetto extends Program
{
	website = "https://github.com/AtesComp/Vinetto";
	package = "app-forensics/vinetto";
	bin     = "vinetto";
	args    = r => ["-o", r.outDir(), "--htmlrep", r.inFile()];
}
