import {Format} from "../../Format.js";

export class autoDeskSketchThumbnail extends Format
{
	name           = "Autodesk SKETCH Thumbnail";
	ext            = [".cad", ".skf"];
	forbidExtMatch = true;
	magic          = [/^Autodesk SKETCH Thumbnail :(qcad|skf):/];
	converters     = ["nconvert[format:qcad]"];
}
