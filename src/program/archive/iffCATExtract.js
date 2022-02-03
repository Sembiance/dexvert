import {xu} from "xu";
import {Program} from "../../Program.js";

export class iffCATExtract extends Program
{
	website   = "https://github.com/Sembiance/iffCATExtract";
	package   = "app-arch/iffCATExtract";
	bin       = "iffCATExtract";
	args      = r => [r.inFile(), r.outDir()];
	renameOut = false;
}
