import {Format} from "../../Format.js";

export class kaboomStudiosBitmapBlock extends Format
{
	name           = "Kaboom Studios Bitmap Block";
	ext            = [".bmb"];
	forbidExtMatch = true;
	magic          = ["Kaboom Studios Bitmap Block"];
	converters     = ["wuimg"];
}
