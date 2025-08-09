import {Format} from "../../Format.js";

export class c33DModel extends Format
{
	name           = "C3 3D model";
	ext            = [".c3"];
	forbidExtMatch = true;
	magic          = [/^3D model$/];
	converters     = ["threeDObjectConverter"];
}
