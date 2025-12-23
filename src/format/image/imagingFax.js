import {Format} from "../../Format.js";

export class imagingFax extends Format
{
	name       = "Imaging Fax";
	website    = "http://fileformats.archiveteam.org/wiki/Imaging_Fax";
	ext        = [".g3n"];
	magic      = ["TIFF :g3n:"];
	converters = ["nconvert[format:g3n]"];
}
