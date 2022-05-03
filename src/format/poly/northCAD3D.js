import {Format} from "../../Format.js";

export class northCAD3D extends Format
{
	name        = "NorthCAD-3D";
	ext         = [".n3d"];
	magic       = ["NorthCAD-3D Drawing"];
	unsupported = true;
}
