import {Format} from "../../Format.js";

export class pdf extends Format
{
	name         = "Portable Document Format";
	website      = "http://fileformats.archiveteam.org/wiki/PDF";
	ext          = [".pdf"];
	mimeType     = "application/pdf";
	magic        = ["Adobe Portable Document Format", "PDF document", "Adobe Portable Document (PDF) Datei", "Format: PDF", /^PDF$/, /Acrobat PDF.* Portable Document Format$/, /^fmt\/(14|15|16|17|18|19|20|95|157|158|276|480)( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => [" PDF", "PDF "].includes(macFileType) && macFileCreator==="CARO";
	untouched    = true;
	metaProvider = ["pdfinfo"];
}
