import {xu} from "xu";
import {Program} from "../../Program.js";

export class musicInfo extends Program
{
	website    = "https://github.com/Sembiance/dexvert/";
	package    = ["media-sound/xmp", "app-emulation/uade", "media-sound/openmpt123", "media-sound/mikmodInfo", "media-sound/timidity++", "media-sound/zxtune", "media-sound/adplay"];
	bin        = "deno";
	args       = r => Program.denoArgs(Program.binPath("musicInfo.js"), "--jsonOutput", "--", r.inFile());
	runOptions = ({env : Program.denoEnv()});
	post       = r => Object.assign(r.meta, xu.parseJSON(r.stdout.trim(), {}));
	renameOut  = false;
}
