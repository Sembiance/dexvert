import {Format} from "../../Format.js";

export class avsx extends Format
{
	name       = "Stardent AVS X";
	website    = "http://fileformats.archiveteam.org/wiki/AVS_X_image";
	ext        = [".avs", ".mbfavs", ".x"];
	mimeType   = "image/x-avsx";
	converters = ["nconvert", "wuimg", `abydosconvert[format:${this.mimeType}]`, "imconv[format:x]", "tomsViewer"];
	verify     = ({meta}) => meta.height>1 && meta.width>1 && meta.colorCount>1;
}
