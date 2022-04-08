import {Format} from "../../Format.js";

export class quickDraw3D extends Format
{
	name       = "QuickDraw 3D Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/3DMF";
	ext        = [".3dmf"];
	magic      = ["QuickDraw 3D Metafile"];
	converters = ["corelPhotoPaint"];
}
