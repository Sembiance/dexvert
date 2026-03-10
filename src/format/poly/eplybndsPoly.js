import {Format} from "../../Format.js";

export class eplybndsPoly extends Format
{
	name           = "EPLYBNDS Poly";
	ext            = [".ply"];
	forbidExtMatch = true;
	magic          = ["EPLYBNDS Poly"];
	converters     = ["threeDObjectConverter[outType:quickDraw3D]"];
}
