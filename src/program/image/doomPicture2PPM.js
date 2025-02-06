import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

const progBasePath = Program.binPath("doomPicture2PPM");

export class doomPicture2PPM extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = async r => Program.denoArgs(path.join(progBasePath, "doomPicture2PPM.js"), `--palette=${path.join(progBasePath, "000.PLAYPAL")}`, r.inFile(), await r.outFile("out.ppm"));	//`--palette=${r.f.aux.palette}`
	runOptions = ({env : Program.denoEnv()});
	renameOut  = true;
	chain      = "convert";
}
