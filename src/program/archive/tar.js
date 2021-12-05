import {Program} from "../../Program.js";

export class tar extends Program
{
	website   = "https://www.gnu.org/software/tar/";
	package   = "app-arch/tar";
	bin       = "tar";
	args      = r => ["-xf", r.inFile(), "-C", r.outDir()];
	renameOut = false;
}
