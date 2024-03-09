import {Format} from "../../Format.js";

export class milkShape3DModel extends Format
{
	name       = "MilkShape 3D Model";
	website    = "http://fileformats.archiveteam.org/wiki/MilkShape_model";
	ext        = [".ms3d"];
	magic      = ["MilkShape 3D model"];
	converters = ["assimp"];
}
