import {Format} from "../../Format.js";

export class doodleAtari extends Format
{
	name          = "Doodle Atari";
	website       = "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)";
	ext           = [".doo", ".art"];
	fileSize      = 32000;
	matchFileSize = true;
	classify      = true;
	converters    = ["deark[module:doodle]", "recoil2png"];	// wuimg works too but is too lax with what it accepts and converts
}
