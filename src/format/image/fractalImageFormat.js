import {Format} from "../../Format.js";

export class fractalImageFormat extends Format
{
	name           = "Fractal Image Format";
	website        = "http://fileformats.archiveteam.org/wiki/FIF_(Fractal_Image_Format)";
	ext            = [".fif"];
	forbidExtMatch = true;
	magic          = ["Fractal Image Format bitmap"];
	converters     = ["fifView"];
	notes          = "The 256C versions don't convert with fifView. I need to track down a different converter that can handle those.";
}
