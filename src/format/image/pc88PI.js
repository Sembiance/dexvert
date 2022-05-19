import {Format} from "../../Format.js";

export class pc88PI extends Format
{
	name       = "NEC PC-88 PI";
	website    = "http://fileformats.archiveteam.org/wiki/Pi_(image_format)";
	ext        = [".pi"];
	magic      = ["Pi bitmap"];
	converters = ["recoil2png"];
}
