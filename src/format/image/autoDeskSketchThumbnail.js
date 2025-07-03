import {Format} from "../../Format.js";

export class autoDeskSketchThumbnail extends Format
{
	name           = "Autodesk SKETCH Thumbnail";
	ext            = [".cad"];
	forbidExtMatch = true;
	magic          = ["Autodesk SKETCH Thumbnail :qcad:"];
	converters     = ["nconvert[format:qcad]"];
}
