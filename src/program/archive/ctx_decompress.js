import {Program} from "../../Program.js";

export class ctx_decompress extends Program
{
	website    = "https://git.fsfe.org/art1pirat/ctxer";
	package    = "app-text/ctxer";
	bin        = "ctx_decompress";
	unsafe     = true;
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}
