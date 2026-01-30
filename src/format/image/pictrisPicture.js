import {Format} from "../../Format.js";

export class pictrisPicture extends Format
{
	name           = "Pictris Picture";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = ["Pictris Picture"];
	converters     = ["wuimg[format:pictris]"];
}
