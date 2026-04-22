import {Format} from "../../Format.js";

export class autoSketchDrawing extends Format
{
	name        = "AutoSketch Drawing";
	ext         = [".skd"];
	magic       = ["AutoSketch Drawing"];
	unsupported = true;	// about 2,309 unique files on discmaster. an initial stab at a vibe coded converter reveals a ton of edge cases and versions and the resulting drawings are mostly IC parts, not very interesting. stopped workg on the converter
}
