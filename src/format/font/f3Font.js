import {Format} from "../../Format.js";

export class f3Font extends Format
{
	name        = "F3 Font";
	website     = "http://fileformats.archiveteam.org/wiki/F3_font";
	ext         = [".f3b"];
	magic       = ["F3 Font", "encrypted scalable OpenFont binary"];
	unsupported = true;
}
