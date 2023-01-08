import {Format} from "../../Format.js";

export class printArtist extends Format
{
	name           = "Print/Instant Artist";
	website        = "http://fileformats.archiveteam.org/wiki/Instant_Artist_GFX";
	ext            = [".gfx"];
	forbidExtMatch = true;
	magic          = ["Print / Instant Artist"];
	converters     = ["printArtist"];
}
