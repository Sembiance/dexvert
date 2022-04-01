import {Program} from "../../Program.js";

export class fshtool extends Program
{
	website   = "http://www.math.polytechnique.fr/cmat/auroux/nfs/";
	package   = "app-arch/fshtool";
	bin       = "fshtool";
	args      = r => [r.inFile(), r.outDir()];
	renameOut = false;
}
