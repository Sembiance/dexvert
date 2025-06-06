import {Format} from "../../Format.js";
import {_PICTUREIT_MAGIC} from "./pictureIt.js";

export class photoDraw extends Format
{
	name           = "PhotoDraw";
	website        = "http://fileformats.archiveteam.org/wiki/MIX_(PhotoDraw)";
	ext            = [".mix"];
	forbidExtMatch = true;
	magic          = ["Microsoft PhotoDraw drawing", /^fmt\/594( |$)/];
	forbiddenMagic = _PICTUREIT_MAGIC;
	converters     = ["photoDraw", "deark[module:cfb]"];	// deark only handles thumbnail extraction
}
