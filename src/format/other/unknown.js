import {xu} from "xu";
import {Format} from "../../Format.js";

export class unknown extends Format
{
	name        = "Unknown File";
	fallback    = true;
	priority    = this.PRIORITY.LOWEST;
	unsupported = true;
	converters  = ["binwalk[all] & foremost"];
	notes       = xu.trim`
		I entertained this idea of a catch-all fallback format that would then use various tools to try and 'extract' out various sub-files like images, audio, etc.
		However these tools are very 'loose' and will extract a LOT of junk. So I'm leaving this out for now.
		If I ever add this back, other tools to consider adding in ADDITION to binwalk & foremost: photorec, testdisk, sleuthkit, magicrescue`;
}
