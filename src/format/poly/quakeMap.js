import {Format} from "../../Format.js";

export class quakeMap extends Format
{
	name           = "Quake Map";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["Quake Map"];
	converters     = ["noesis[type:poly]"];
}
