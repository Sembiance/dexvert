import {Format} from "../../Format.js";

export class triangleDAT extends Format
{
	name           = "Triangle DAT";
	ext            = [".dat", ".ff", ".art"];
	forbidExtMatch = true;
	magic          = ["archive:Triangle.DatOpener"];
	weakMagic      = true;
	converters     = ["GARbro[types:archive:Triangle.DatOpener]"];
}
