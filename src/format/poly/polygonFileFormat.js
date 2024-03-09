import {Format} from "../../Format.js";

export class polygonFileFormat extends Format
{
	name       = "Polygon File Format";
	website    = "http://fileformats.archiveteam.org/wiki/PLY";
	ext        = [".ply"];
	magic      = ["PLY model", "Polygon File Format", /^fmt\/831( |$)/];
	converters = ["assimp", "blender[format:ply]"];
}
