import {Format} from "../../Format.js";

export class quake2Map extends Format
{
	name           = "Quake II Map";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["Quake2 map", "Quake II Map file"];
	converters     = ["noesis[type:poly]"];
}
