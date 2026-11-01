import {Format} from "../../Format.js";

export class triangleDAT extends Format
{
	name           = "Triangle DAT";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["archive:Triangle.DatOpener"];
	converters     = ["GARbro[types:archive:Triangle.DatOpener]"];
}
