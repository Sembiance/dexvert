import {Format} from "../../Format.js";

export class eclipseTILE extends Format
{
	name           = "Eclipse TILE bitmap";
	ext            = [".tile"];
	forbidExtMatch = true;
	magic          = ["Eclipse TILE bitmap"];
	converters     = ["wuimg"];
}
