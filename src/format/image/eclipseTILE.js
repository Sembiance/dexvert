import {Format} from "../../Format.js";

export class eclipseTILE extends Format
{
	name           = "Eclipse TILE bitmap";
	ext            = [".tile"];
	forbidExtMatch = true;
	magic          = ["Eclipse TILE bitmap", "Eclipse :tile:"];
	converters     = ["wuimg[format:eclipse]"];	// nconvert despite detecting this format, doesn't convert them correctly
}
