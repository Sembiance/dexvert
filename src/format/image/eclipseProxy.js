import {Format} from "../../Format.js";

export class eclipseProxy extends Format
{
	name           = "Eclipse Proxy";
	ext            = [".pxy"];
	forbidExtMatch = true;
	magic          = ["Eclipse Proxy Image"];
	weakMagic      = true;
	converters     = ["wuimg"];
}
