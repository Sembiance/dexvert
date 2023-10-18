import {Format} from "../../Format.js";

export class ansiMusic extends Format
{
	name           = "ANSI Music";
	website        = "http://artscene.textfiles.com/ansimusic/";
	ext            = [".mus"];
	forbidExtMatch = true;
	magic          = ["ANSI escape sequence text", "ISO-8859 text, with CRLF, CR, LF line terminators, with escape sequences"];
	weakMagic      = true;
	unsupported    = true;
	notes          = "No known converter. Maybe easiest would be converting to MIDI? More info and samples from: http://artscene.textfiles.com/ansimusic/";
}
