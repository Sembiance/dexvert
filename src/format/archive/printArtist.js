import {Format} from "../../Format.js";

export class printArtist extends Format
{
	name           = "Print/Instant Artist";
	website        = "http://fileformats.archiveteam.org/wiki/Print_Artist";
	ext            = [".gfx"];
	forbidExtMatch = true;
	magic          = ["Print / Instant Artist"];
	slow           = true;
	converters     = ["printArtist"];
}
