import {Format} from "../../Format.js";

export class smoothMovePanViewerImage extends Format
{
	name           = "SmoothMove Pan Viewer Image";
	ext            = [".pan"];
	forbidExtMatch = true;
	magic          = ["SmoothMove Pan Viewer :pan:"];
	converters     = ["nconvert[format:pan]"];
}
