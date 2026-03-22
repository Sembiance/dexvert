import {Format} from "../../Format.js";

export class doodleAtari extends Format
{
	name          = "Doodle Atari";
	website       = "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)";
	magic         = ["deark: doodle", "Doodle Atari :doodle:"];
	ext           = [".doo", ".art"];
	mimeType      = "image/x-dr-doodle";
	fileSize      = 32000;
	matchFileSize = true;
	classify      = true;
	converters    = ["deark[module:doodle]", "recoil2png[format:ART.Doo,DOO]", "nconvert[format:doodle]", `abydosconvert[format:${this.mimeType}]`];	// wuimg works too but is too lax with what it accepts and converts
}
