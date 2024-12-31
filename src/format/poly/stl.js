import {Format} from "../../Format.js";

export class stl extends Format
{
	name    = "STereoLithography";
	website = "http://fileformats.archiveteam.org/wiki/STL";
	ext     = [".stl"];
	magic   = [
		// generic
		"STereoLithography", "model/stl", /^x-fmt\/108( |$)/,
		
		// specific
		"Blender exported STereoLithography", "libthing STereoLithography", "VCGLib STereoLithography", "NetFabb STereoLithography", "OpenSCAD STereoLithography", "ATF STereoLithography", "FreeCAD STereoLithography", "3DSMax STereoLithography",
		"Blender STereoLithography", "Cura STereoLithography", "MeshLab STereoLithography", "Meshmixer STereoLithography", "Rhinoceros STereoLithography", "Digitized Shape Editor/CATIA STereoLithography", "AutoCAD STereoLithography"
	];
	converters = ["blender[format:stl]", "assimp"];
}
