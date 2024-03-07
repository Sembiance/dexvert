import {Format} from "../../Format.js";

export class pdf extends Format
{
	name         = "Portable Document Format";
	website      = "http://fileformats.archiveteam.org/wiki/PDF";
	ext          = [".pdf"];
	mimeType     = "application/pdf";
	magic        = ["Adobe Portable Document Format", "PDF document", "Adobe Portable Document (PDF) Datei", /^PDF$/, /Acrobat PDF.* Portable Document Format$/, /^fmt\/(18|19)( |$)/];
	untouched    = true;
	metaProvider = ["pdfinfo"];
}
