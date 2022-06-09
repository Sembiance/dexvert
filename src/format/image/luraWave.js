import {Format} from "../../Format.js";

export class luraWave extends Format
{
	name           = "LuRaWave Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/LuraWave";
	ext            = [".lwf"];
	forbidExtMatch = true;
	magic          = ["LuraWave Format bitmap"];
	converters     = ["luraWave"];
}
