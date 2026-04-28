import {Format} from "../../Format.js";

export class keyCADCompleteDrawing extends Format
{
	name        = "KeyCAD Complete Drawing";
	ext         = [".kcf"];
	magic       = ["KeyCAD Complete drawing"];
	unsupported = true;	// only 20 unique files on discmaster
}
