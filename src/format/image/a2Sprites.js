import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class a2Sprites extends Format
{
	name        = "Apple II Sprites";
	ext         = [".spr"];
	magic       = TEXT_MAGIC;
	weakMagic   = true;
	unsupported = true;
	notes       = "Currently marked as unsupported because I can only really match extension and recoil2png isn't picky about what it converts resulting in a lot of 'garbage' output. Only have 1 sample file, so pretty rare format.";
	converters  = ["recoil2png[format:SPR.AppleSpr]"];
	verify      = ({meta}) => meta.colorCount>1;
}
