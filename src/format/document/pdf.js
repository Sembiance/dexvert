import {Format} from "../../Format.js";

export class pdf extends Format
{
	name         = "Portable Document Format";
	website      = "http://fileformats.archiveteam.org/wiki/PDF";
	ext          = [".pdf"];
	mimeType     = "application/pdf";
	magic        = ["Adobe Portable Document Format", "PDF document", /Acrobat PDF.* Portable Document Format$/];
	untouched    = true;
	metaProvider = ["pdfinfo"];
}
