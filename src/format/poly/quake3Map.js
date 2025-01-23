import {Format} from "../../Format.js";

export class quake3Map extends Format
{
	name           = "Quake III Map";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["Quake III Map file"];
	converters     = ["noesis[type:poly]"];
}
