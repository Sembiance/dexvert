import {Format} from "../../Format.js";

export class cdr extends Format
{
	name           = "CorelDraw Document";
	website        = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	ext            = [".cdr", ".cdt", ".cdx", ".cpx"];
	forbidExtMatch = [".cpx"];
	magic          = ["CorelDraw Document", "CorelDraw Drawing", "CorelDRAW for OS/2 drawing", /^fmt\/(464|466)( |$)/, /^x-fmt\/(291|379)( |$)/];
	converters     = ["scribus", "deark", "nconvert", "corelDRAW", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas"];
}
