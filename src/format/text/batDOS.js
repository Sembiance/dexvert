import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class batDOS extends Format
{
	name           = "DOS Batch File";
	website        = "http://fileformats.archiveteam.org/wiki/Batch_file";
	ext            = [".bat"];
	forbidExtMatch = true;
	magic          = ["DOS batch file", "BAT/CMD Batch Datei", ...TEXT_MAGIC, /^data$/];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
