import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class a2Sprites extends Format
{
	name        = "Apple II Sprites";
	ext         = [".spr"];
	magic       = TEXT_MAGIC;
	weakMagic   = true;
	unsupported = true;	// only 1 sample, only ext match, recoil produces garbage with invalid files
	converters  = ["recoil2png[format:SPR.AppleSpr]"];
	verify      = ({meta}) => meta.colorCount>1;
}
