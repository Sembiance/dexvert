import {Format} from "../../Format.js";

export class pdf extends Format
{
	name         = "Portable Document Format";
	website      = "http://fileformats.archiveteam.org/wiki/PDF";
	ext          = [".pdf"];
	mimeType     = "application/pdf";
	magic        = [
		"Adobe Portable Document Format", "PDF document", "Adobe Portable Document (PDF) Datei", "Format: PDF", "application/pdf", /^PDF$/, /Acrobat PDF.* Portable Document Format$/,
		/^fmt\/(14|15|16|17|18|19|20|95|146|157|158|276|354|477|479|480|488|558|559|560|561|562|563|564|565|1451|1862)( |$)/		// 1862 is actually an Adobe Illustrator format but modern and can't convert but it has a built in PDF preview, so this works
	];
	idMeta       = ({macFileType, macFileCreator}) => [" pdf", "pdf ", "pdf?", "pdf□"].includesAny([macFileType?.toLowerCase(), macFileCreator?.toLowerCase()]);
	untouched    = true;
	metaProvider = ["pdfinfo"];
}
