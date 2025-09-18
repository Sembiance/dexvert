import {Format} from "../../Format.js";

export class fenixMap extends Format
{
	name           = "Fenix Map";
	ext            = [".map"];
	forbidExtMatch = true;
	magic          = ["Fenix Map :map:"];
	converters     = ["nconvert[format:map]"];
}
