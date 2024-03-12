import {Format} from "../../Format.js";

export class simply3DGeometry extends Format
{
	name       = "Simply 3D Geometry";
	website    = "http://fileformats.archiveteam.org/wiki/Simply_3D_Geometry";
	ext        = [".ged"];
	magic      = ["Simply 3D Geometry"];
	converters = ["simply3D20"];
}
