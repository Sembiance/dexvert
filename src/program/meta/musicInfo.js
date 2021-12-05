import {xu} from "xu";
import {Program} from "../../Program.js";

export class musicInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/blob/master/bin/modInfo.js";
	package = ["media-sound/xmp", "app-emulation/uade", "media-sound/openmpt123", "media-sound/mikmodInfo", "media-sound/timidity++"];
	bin     = Program.binPath("musicInfo");
	args    = r => ["--jsonOutput", "--", r.inFile()];
	post    = r => Object.assign(r.meta, xu.parseJSON(r.stdout.trim(), {}));
}
