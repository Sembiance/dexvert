import {Format} from "../../Format.js";

export class cdr extends Format
{
	name           = "CorelDraw Document";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".cdr", ".cdt", ".cdx", ".cpx"];
	forbidExtMatch = [".cpx"];
	magic          = ["CorelDraw Document", "CorelDraw Drawing", "CorelDRAW for OS/2 drawing", "CorelDraw compressed format", /^fmt\/(464|466)( |$)/, /^x-fmt\/(31|36|291|379)( |$)/];
	converters     = ["scribus", "deark[module:cdr_wl]", "nconvert", "corelDRAW", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas"];
}
