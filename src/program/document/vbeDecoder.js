import {Program} from "../../Program.js";
import {path} from "std";

export class vbeDecoder extends Program
{
	website   = "https://github.com/JohnHammond/vbe-decoder";
	bin       = "python3";
	unsafe    = true;
	args      = async r => [path.join(Program.binPath("vbe-decoder"), "vbe-decoder.py"), "-o", await r.outFile("out.vb"), r.inFile()];
	renameOut = true;
}
