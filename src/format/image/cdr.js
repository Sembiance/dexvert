import {Format} from "../../Format.js";

export class cdr extends Format
{
	name           = "CorelDraw Document";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".cdr", ".cdt", ".cdx", ".cpx"];
	forbidExtMatch = [".cpx"];
	magic          = ["CorelDraw Document", "CorelDraw Drawing", "CorelDRAW for OS/2 drawing", "CorelDraw compressed format", /RIFF Datei: unbekannter Typ 'CDR[ \d]'/, /^Corel Draw Picture, version \d\.0/, /^fmt\/(464|466|1926)( |$)/, /^x-fmt\/(31|36|291|379)( |$)/];
	converters     = [
		// vector
		"scribus",
		
		// raster
		"photoDraw", "nconvert", "corelDRAW", "deark[module:cdr_wl]", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas"
	];
}
