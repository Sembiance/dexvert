import {Format} from "../../Format.js";

export class maxisXA extends Format
{
	name         = "Maxis XA Audio";
	website      = "https://wiki.multimedia.cx/index.php/Maxis_XA";
	ext          = [".xa"];
	magic        = ["Maxis XA Audio", "RIFF Datei: unbekannter Typ 'CDXA'", "Generic RIFF file CDXA", "Maxis XA (xa)", /^geViewer: DAT_DBPF_XA_XA( |$)/, /^soxi: xa$/];
	metaProvider = ["soxi"];
	converters   = ["sox[type:xa]", "vgmstream", "zxtune123"];
}
