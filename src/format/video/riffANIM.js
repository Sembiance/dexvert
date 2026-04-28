import {Format} from "../../Format.js";

export class riffANIM extends Format
{
	name        = "RIFF ANIM";
	ext         = [".paf"];
	magic       = ["RIFF ANIM file", "PAF Animation Format"];
	unsupported = true;	// this actually identifies to at least 3 DIFFERENT RIFF ANIM formats on discmaster. A vibe converter was started but abandoned (see vibe/legacy/riffANIM/)
}
