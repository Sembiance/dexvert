import {Format} from "../../Format.js";

export class imageSystem extends Format
{
	name    = "Image System";
	website = "http://fileformats.archiveteam.org/wiki/Image_System";
	ext     = [".ish", ".ism"];

	// recoil2png doesn't properly handle some files, nconvert does a better job here
	converters = ["nconvert", "recoil2png", "view64"];

	// Due to not having a good magic, we reject any created images that have less than 5 colors
	verify = ({meta}) => meta.colorCount>5;
}
