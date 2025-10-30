import {Format} from "../../Format.js";

export class halfLifeMap extends Format
{
	name           = "Half-Life Map";
	ext            = [".bsp"];
	forbidExtMatch = true;
	magic          = ["Half-Life map"];
	converters     = ["noesis[type:poly]"];
}
