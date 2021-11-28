import {Format} from "../../Format.js";

export class crackArt extends Format
{
	name       = "Crack Art";
	website    = "http://fileformats.archiveteam.org/wiki/Crack_Art";
	ext        = [".ca1", ".ca2", ".ca3"];
	magic      = ["Crack Art bitmap"];
	converters = ["recoil2png"];
}
