import {Format} from "../../Format.js";

export class asciiArtEditor extends Format
{
	name       = "Ascii-Art Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Ascii-Art_Editor";
	ext        = [".art"];
	converters = ["recoil2png"];
}
