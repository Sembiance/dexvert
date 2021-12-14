import {Program} from "../../Program.js";

export class gsPDFInfo extends Program
{
	website = "https://ghostscript.com/";
	package = "app-text/ghostscript-gpl";
	bin     = "gs";
	notes   = "Only getting bounding box info for now";
	args    = r => ["-dBATCH", "-dNOPAUSE", "-dQUIET", "-sDEVICE=bbox", r.inFile()];
	post    = r =>
	{
		r.meta.boundingBoxes = r.stderr.split("\n").filter(v => v.startsWith("%%BoundingBox:"));
	};
	renameOut = false;
}
