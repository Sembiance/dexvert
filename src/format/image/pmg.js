import {Format} from "../../Format.js";

export class pmg extends Format
{
	name       = "Paint Magic";
	website    = "http://fileformats.archiveteam.org/wiki/Paint_Magic";
	ext        = [".pmg"];

	// Because it just matches a generic extension, a size check will help ensure we don't try and convert crazyiness
	// Only have 1 known sample and it's less than 10k, so just try that
	idCheck = inputFile => inputFile.size<10000;

	converters = ["recoil2png", "view64"];
}
