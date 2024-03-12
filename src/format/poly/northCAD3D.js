import {Format} from "../../Format.js";

export class northCAD3D extends Format
{
	name        = "NorthCAD-3D";
	ext         = [".n3d"];
	magic       = ["NorthCAD-3D Drawing"];
	unsupported = true;
	notes       = "Only 10 unique files on all of discmaster and all seem to just be samples provided from the program itself. Not worth supporting right now";
}
