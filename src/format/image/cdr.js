import {Format} from "../../Format.js";

export class cdr extends Format
{
	name           = "CorelDraw Document";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".cdr", ".cdt", ".cdx", ".cpx"];
	forbidExtMatch = [".cpx"];
	magic          = ["CorelDraw Document", "CorelDraw Drawing", "Corel Draw drawing", "CorelDRAW for OS/2 drawing", "CorelDraw compressed format", "Format: CorelDraw graphics", /^Corel Draw \d Grafikdatei \(CDR\)$/,
		/^RIFF (little-endian) data, Corel Draw Picture/, /RIFF Datei: unbekannter Typ 'CDR[ \d]'/, /^Corel Draw Picture, version \d\.0/, /^fmt\/(464|465|466|1926)( |$)/, /^x-fmt\/(29|31|36|291|379)( |$)/];
	converters     = [
		// vector
		"scribus",
		"canvas5[vector]",
		
		// raster
		"photoDraw", "nconvert", "corelDRAW", "deark[module:cdr_wl]", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas"
	];
}
