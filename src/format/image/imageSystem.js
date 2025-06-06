import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class imageSystem extends Format
{
	name           = "Image System";
	website        = "http://fileformats.archiveteam.org/wiki/Image_System";
	ext            = [".ish", ".ism"];
	magic          = [/^Image System \((Hires|Multicolor)\) :cis[hm]:$/];
	fileSize       = {".ism" : 10218};
	matchFileSize  = true;
	forbiddenMagic = TEXT_MAGIC;

	// recoil2png doesn't properly handle some files, nconvert does a better job here
	converters = ["nconvert[format:cism]", "nconvert[format:cish]", "recoil2png", "view64"];

	// Due to not having a good magic, we reject any created images that have less than 5 colors
	verify = ({meta}) => meta.colorCount>5;
}
