import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class paintPro extends Format
{
	name           = "PaintPro";
	website        = "http://fileformats.archiveteam.org/wiki/PaintPro";
	ext            = [".pic"];
	fileSize       = 32034;
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png"];
}
