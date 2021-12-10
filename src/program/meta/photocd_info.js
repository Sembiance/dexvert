import {xu} from "xu";
import {Program} from "../../Program.js";

export class photocd_info extends Program
{
	website    = "https://github.com/Sembiance/dexvert";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("photocd-info.js"), "--", r.inFile());
	runOptions = ({env : Program.denoEnv()});
	post       = r => Object.assign(r.meta, xu.parseJSON(r.stdout.trim(), {}));
	renameOut  = false;
}
