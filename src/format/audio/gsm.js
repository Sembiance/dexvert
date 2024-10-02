import {Format} from "../../Format.js";

export class gsm extends Format
{
	name         = "GSM Audio";
	website      = "http://fileformats.archiveteam.org/wiki/GSM";
	ext          = [".gsm"];
	magic        = ["raw GSM (gsm)"];
	weakMagic    = ["raw GSM (gsm)"];
	metaProvider = ["soxi"];
	converters   = ["sox"];	// ffmpeg[format:gsm][outType:mp3] also works, but it'll convert any ole .gsm file into garbage and sox handles all the file samples without converting garbage, so just use sox
}
