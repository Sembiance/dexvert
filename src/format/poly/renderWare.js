import {xu} from "xu";
import {Format} from "../../Format.js";

export class renderWare extends Format
{
	name       = "RenderWare 3D Model";
	website    = "http://fileformats.archiveteam.org/wiki/RenderWare_object";
	ext        = [".rwx"];
	magic      = ["RenderWare 3d model"];
	converters = ["AccuTrans3D"];
}
