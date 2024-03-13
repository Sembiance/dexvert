import {Format} from "../../Format.js";

export class faxx extends Format
{
	name       = "Facsimile image FORM";
	website    = "http://fileformats.archiveteam.org/wiki/FAXX";
	ext        = [".faxx", ".fax"];
	mimeType   = "image/x-faxx";
	magic      = ["MultiFax FAX", "IFF data, FAXX", "IFF Facsimile image"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
