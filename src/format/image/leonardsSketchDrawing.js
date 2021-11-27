import {Format} from "../../Format.js";

export class leonardsSketchDrawing extends Format
{
	name        = "LEONARD'S Sketch Drawing";
	ext         = [".ogf"];
	magic       = ["LEONARD'S Sketch drawing"];
	unsupported = true;
	notes       = "Fairly obscure CAD type drawing program. Not aware of any drawings that were not those that were included with the program, so format not worth supporting.";
}
