import {Format} from "../../Format.js";

export class avsx extends Format
{
	name       = "Stardent AVS X";
	website    = "http://fileformats.archiveteam.org/wiki/AVS_X_image";
	ext        = [".avs", ".mbfavs", ".x"];
	mimeType   = "image/x-avsx";
	converters = ["nconvert", `abydosconvert[format:${this.mimeType}]`];
}
