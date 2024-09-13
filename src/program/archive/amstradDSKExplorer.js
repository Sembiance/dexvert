import {Program} from "../../Program.js";
import {path} from "std";

export class amstradDSKExplorer extends Program
{
	website   = "https://github.com/muckypaws/AmstradDSKExplorer";
	bin       = "python";
	args      = r => [path.join(Program.binPath("AmstradDSKExplorer"), "DSKInfoV3.py"), "-dir", "-ex", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
