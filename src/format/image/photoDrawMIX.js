import {Format} from "../../Format.js";
import {_PICTUREIT_MAGIC} from "./pictureItMIX.js";

export class photoDrawMIX extends Format
{
	name           = "PhotoDraw MIX";
	website        = "http://fileformats.archiveteam.org/wiki/MIX_(PhotoDraw)";
	ext            = [".mix"];
	forbidExtMatch = true;
	magic          = ["Microsoft PhotoDraw drawing", /^fmt\/594( |$)/];
	forbiddenMagic = _PICTUREIT_MAGIC;
	converters     = ["photoDraw", "deark[module:cfb]", "nconvert"];	// deark and nconvert only handle thumbnail extraction
}
