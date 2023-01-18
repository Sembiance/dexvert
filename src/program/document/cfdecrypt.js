import {Program} from "../../Program.js";

export class cfdecrypt extends Program
{
	website    = "https://github.com/disccomp/cfdecrypt";
	bin        = Program.binPath("cfdecrypt/cfdecrypt.sh");
	args       = async r => ["-o", await r.outFile("out"), r.inFile()];
	renameOut  = true;
}
