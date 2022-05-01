import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {_IMF_MAGIC} from "../text/imf.js";

export class ans extends Format
{
	name           = "ANSI Art File";
	website        = "http://fileformats.archiveteam.org/wiki/ANSI_Art";
	ext            = [".ans", ".drk", ".ice", ".ansi", ".asc", ".gbs"];
	weakExt        = [".drk", ".ice", ".asc"];	// .ANS was widely accepted as ANSI, but .drk and .ice less so. .asc is also not widely used.
	// Sadly some .ice files like "2002 - 20 - tcf-0001.ice" won't get converted because they only identify as 'data' and since ansilive will convert any file you send into it, we can't send it these
	forbidExtMatch = true;
	mimeType       = "text/x-ansi";
	priority       = this.PRIORITY.LOW;	// allow other image format detections to take priority
	magic          = ["ANSI escape sequence text", "ISO-8859 text, with escape sequences", ...TEXT_MAGIC, /^data$/, ..._IMF_MAGIC];
	weakMagic      = ["ISO-8859 text, with escape sequences", ...TEXT_MAGIC, /^data$/, ..._IMF_MAGIC];
	metaProvider   = ["ansiArt"];
	converters     = [
		"ansilove[format:ans]",
		"deark[module:ansiart]",
		dexState => (dexState.imageFailedTooTall ? null : "ffmpeg[format:tty][codec:ansi][outType:gif]")	// if we failed a previous converter due to being too tall, then don't convert to an animated GIF (text/txt/Newsletter)
	];
}
