import {Format} from "../../Format.js";

export class bisP3DMLODModel extends Format
{
	name       = "BIS P3D MLOD model";
	website    = "http://community.bistudio.com/wiki/P3D_File_Format_-_MLOD";
	ext        = [".p3d"];
	magic      = ["BIS P3D MLOD model"];
	converters = ["threeDObjectConverter"];
}
