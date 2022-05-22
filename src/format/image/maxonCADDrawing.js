import {Format} from "../../Format.js";

export class maxonCADDrawing extends Format
{
	name        = "MaconCAD Drawing";
	ext         = [".mc2"];
	magic       = ["MaxonCAD 2 drawing"];
	unsupported = true;
}
