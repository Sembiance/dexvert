import {Format} from "../../Format.js";

export class stl extends Format
{
	name       = "STereoLithography";
	website    = "http://fileformats.archiveteam.org/wiki/STL";
	ext        = [".stl"];
	magic      = ["Blender exported STereoLithography", "STereoLithography", "VCGLib STereoLithography", "NetFabb STereoLithography", "OpenSCAD STereoLithography", "ATF STereoLithography", "FreeCAD STereoLithography", /^x-fmt\/108( |$)/];
	converters = ["blender[format:stl]", "assimp"];
}
