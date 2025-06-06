import {Format} from "../../Format.js";

export class texPKFont extends Format
{
	name       = "Packed Font File Format";
	website    = "http://fileformats.archiveteam.org/wiki/PK_font";
	ext        = [".pk"];
	filename   = [/\d+pk$/i];
	magic      = ["GFtoPK packed font", "deark: pkfont", /^application\/x-font-tex$/, /TeX [Pp]acked font data/];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType==="Tfm+" && macFileCreator==="TeX+") || (macFileType==="OzPK" && macFileCreator==="OzMF");
	converters = ["deark[module:pkfont]"];
}
