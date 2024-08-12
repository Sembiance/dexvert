import {Format} from "../../Format.js";

export class riffANIM extends Format
{
	name        = "RIFF ANIM";
	ext         = [".paf"];
	magic       = ["RIFF ANIM file", "PAF Animation Format"];
	unsupported = true;
	notes       = "Couldn't find any evidence of this out in the public. Could very well be a proprietary format";
}
