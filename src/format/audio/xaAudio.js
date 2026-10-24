import {Format} from "../../Format.js";

export class xaAudio extends Format
{
	name         = "XA Audio";
	website      = "https://wiki.multimedia.cx/index.php/Maxis_XA";
	ext          = [".xa"];
	magic        = ["Maxis XA Audio", "RIFF Datei: unbekannter Typ 'CDXA'", "Generic RIFF file CDXA", "Maxis XA (xa)", /^soxi: xa$/, "vgmstream: xa ", "vgmstream: maxis_xa"];
	metaProvider = ["soxi"];
	converters   = ["sox[type:xa]", "vgmstream[types:xa,maxis_xa]", "zxtune123"];
}
