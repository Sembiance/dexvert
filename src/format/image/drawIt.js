import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class drawIt extends Format
{
	name           = "DrawIt";
	ext            = [".dit"];
	fileSize       = 3845;
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png"];
}
