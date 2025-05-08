import {Format} from "../../Format.js";

export class cdr extends Format
{
	name           = "CorelDraw Document";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".cdr", ".cdt", ".cdx", ".cpx"];
	forbidExtMatch = [".cpx"];
	magic          = ["CorelDraw Document", "CorelDraw Drawing", "Corel Draw drawing", "CorelDRAW for OS/2 drawing", "CorelDraw compressed format", "Format: CorelDraw graphics", "application/vnd.corel-draw", /^Corel Draw \d Grafikdatei \(CDR\)$/,
		/^Generic RIFF file CDR[5 ]$/,
		/^Corel Draw \d Templatedatei \(CDT\)/, /^RIFF (little-endian) data, Corel Draw Picture/, /RIFF Datei: unbekannter Typ 'CDR[ \d]'/, /^Corel Draw Picture, version \d\.0/, /^fmt\/(427|428|464|465|466|1925|1926)( |$)/, /^x-fmt\/(29|31|36|291|292|374|375|378|379)( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["CDR ", "CDT6", "CDR6", "CDR8"].includes(macFileType) && macFileCreator==="Cdrw";
	converters     = [
		// vector
		"scribus",
		"canvas5[vector]",
		
		// raster
		"photoDraw", "nconvert", "corelDRAW", "deark[module:cdr_wl]", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas"
	];
}
