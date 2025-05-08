import {Format} from "../../Format.js";

export class maxisXA extends Format
{
	name         = "Maxis XA Audio";
	website      = "https://wiki.multimedia.cx/index.php/Maxis_XA";
	ext          = [".xa"];
	magic        = ["Maxis XA Audio", "RIFF Datei: unbekannter Typ 'CDXA'", "Generic RIFF file CDXA", "Maxis XA (xa)", /^soxi: xa$/];
	metaProvider = ["soxi"];
	converters   = ["sox", "vgmstream", "zxtune123"];
}
