import {Format} from "../../Format.js";

export class imagingFax extends Format
{
	name       = "Imaging Fax";
	ext        = [".g3n"];
	magic      = ["TIFF :g3n:"];
	converters = ["nconvert[format:g3n]"];
}
