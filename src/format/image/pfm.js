import {Format} from "../../Format.js";

export class pfm extends Format
{
	name         = "Portable Float Map";
	website      = "http://fileformats.archiveteam.org/wiki/PFM_(Portable_Float_Map)";
	ext          = [".pfm"];
	mimeType     = "image/x-portable-floatmap";
	magic        = ["Portable Float Map color bitmap"];
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "nconvert", "tomsViewer"];
}
