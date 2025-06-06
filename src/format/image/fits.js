import {Format} from "../../Format.js";

export class fits extends Format
{
	name       = "Flexible Image Transport System";
	website    = "http://fileformats.archiveteam.org/wiki/Flexible_Image_Transport_System";
	ext        = [".fit", ".fits", ".fts", ".fz"];
	mimeType   = "image/fits";
	magic      = ["Flexible Image Transport System", "FITS image data", "application/fits", "Flexible Image Transport System :fits:",  /^x-fmt\/383( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="FITS" && macFileCreator==="VIST";
	converters = ["nconvert[format:fits]", "iconvert", "gimp"];
}
