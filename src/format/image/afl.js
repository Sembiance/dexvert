import {Format} from "../../Format.js";

export class afl extends Format
{
	name        = "AFLI-Editor Image";
	website     = "http://fileformats.archiveteam.org/wiki/AFLI-Editor";
	ext         = [".afl", ".afli"];
	unsupported = true;
	notes       = "Due to not having any 'MAGIC' identification or specific file size? and the rarity of any user files in the wild and that recoil+view64 will convert almost any .afl into a garbage output, dexvert doesn't support converting this file.";
	converters  = ["recoil2png[format:AFL]", "view64"];
}
