import {Format} from "../../Format.js";

export class viff extends Format
{
	name         = "Khoros Visualization Image";
	website      = "http://fileformats.archiveteam.org/wiki/VIFF";
	ext          = [".viff", ".xv"];
	mimeType     = "image/x-viff";
	magic        = ["Khoros Visualization Image File Format"];
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "imconv[format:viff]", "tomsViewer"];
}
