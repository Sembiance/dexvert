import {Program} from "../../Program.js";

export class uudecode extends Program
{
	website   = "https://www.gnu.org/software/sharutils/";
	package   = "app-arch/sharutils";
	bin       = Program.binPath("uudecodeWithDirs.sh");
	args      = r => [r.inFile({absolute : true})];
	cwd       = r => r.outDir({absolute : true});
	renameOut = false;
}
