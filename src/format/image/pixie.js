import {Format} from "../../Format.js";

export class pixie extends Format
{
	name        = "Pixie Vector";
	website     = "http://fileformats.archiveteam.org/wiki/Pixie_(vector_graphics)";
	ext         = [".pxi", ".pxs"];
	magic       = ["Pixie vector graphic"];
	unsupported = true;
}
