import {Format} from "../../Format.js";

export class northCAD3D extends Format
{
	name        = "NorthCAD-3D";
	website     = "http://fileformats.archiveteam.org/wiki/SGI_YAODL";
	ext         = [".n3d"];
	magic       = ["NorthCAD-3D Drawing"];
	unsupported = true;
}
