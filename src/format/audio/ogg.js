import {Format} from "../../Format.js";

export class ogg extends Format
{
	name         = "Ogg Vorbis Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Ogg";
	ext          = [".ogg", ".oga"];
	magic        = ["OGG Vorbis audio", "Ogg data, Vorbis audio", /^fmt\/203( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
