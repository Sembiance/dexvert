import {xu} from "xu";
import {Program} from "../../Program.js";

export class maconv extends Program
{
	website   = "https://github.com/ParksProjets/Maconv";
	package   = "app-arch/maconv";
	bin       = "maconv";
	args      = r => ["e", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
