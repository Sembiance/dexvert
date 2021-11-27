import {Format} from "../../Format.js";

export class pcDraftCAD extends Format
{
	name           = "PC-Draft-CAD Drawing";
	ext            = [".dwg"];
	forbidExtMatch = true;
	magic          = ["PC-Draft-CAD drawing"];
	unsupported    = true;
}
