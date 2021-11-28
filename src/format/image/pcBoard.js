import {Format} from "../../Format.js";

export class pcBoard extends Format
{
	name           = "PC-Board";
	website        = "http://fileformats.archiveteam.org/wiki/PCBoard";
	forbidExtMatch = true;
	ext            = [".pcb"];
	mimeType       = "text/x-pcboard";
	magic          = [/^data$/, "ISO-8859 text"];
	weakMagic      = true;
	metaProvider   = ["ansiArt"];
	
	// We do NOT use abydos, because it just falls back to ansilove
	converters = ["ansilove"];
}
