import {Format} from "../../Format.js";

export class zoopGameGraphics extends Format
{
	name           = "Zoop game graphics";
	ext            = [".imx"];
	forbidExtMatch = true;
	magic          = ["Zoop game graphics"];
	converters     = ["xor[hex:AA] -> nconvert[format:pcx]"];
}
