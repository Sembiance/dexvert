import {xu} from "xu";
import {Program} from "../../Program.js";

export class musicInfo extends Program
{
	website    = "https://github.com/Sembiance/dexvert/";
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("musicInfo.js"), "--jsonOutput", "--", r.inFile());
	runOptions = ({env : Program.denoEnv()});
	post       = r => Object.assign(r.meta, xu.parseJSON(r.stdout.trim(), {}));
}
