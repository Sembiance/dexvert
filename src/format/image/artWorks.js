import {Format} from "../../Format.js";

export class artWorks extends Format
{
	name       = "ArtWorks Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/Artworks";
	magic      = ["ArtWorks drawing"];
	converters = ["vibe2svg"];
}
