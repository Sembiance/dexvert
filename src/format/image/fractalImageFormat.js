import {Format} from "../../Format.js";

export class fractalImageFormat extends Format
{
	name           = "Fractal Image Format";
	website        = "http://fileformats.archiveteam.org/wiki/FIF_(Fractal_Image_Format)";
	ext            = [".fif"];
	forbidExtMatch = true;
	magic          = ["Fractal Image Format bitmap"];
	converters     = ["fifView"];
}
