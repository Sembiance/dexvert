import {xu} from "xu";
import {Format} from "../../Format.js";

export class fmTownsHEL extends Format
{
	name           = "FM-Towns HEL Animation";
	ext            = [".hel"];
	forbidExtMatch = true;
	magic          = ["FM Towns HEL bitmap", "FM-Towns HEL Animation"];
	converters     = ["hel2tif -> *ffmpeg[fps:8][outType:gif]"];
}
