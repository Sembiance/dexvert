import {Format} from "../../Format.js";

export class jingTaoPicFormatBitmap extends Format
{
	name           = "Jing Tao pic format bitmap";
	ext            = [".ssl"];
	forbidExtMatch = true;
	magic          = ["Jing Tao pic format bitmap"];
	converters     = ["jingTaoPic2jpg[matchType:magic]"];
}
