import {Format} from "../../Format.js";

export class faceSaver extends Format
{
	name       = "FaceSaver";
	website    = "http://fileformats.archiveteam.org/wiki/FaceSaver";
	ext        = [".face", ".fac"];
	mimeType       = "image/x-facesaver";
	magic      = ["FaceSaver bitmap"];
	converters = ["fstopgm", `abydosconvert[format:${this.mimeType}]`];
}
