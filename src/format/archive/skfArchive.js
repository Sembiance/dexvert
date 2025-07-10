import {xu} from "xu";
import {Format} from "../../Format.js";

export class skfArchive extends Format
{
	name           = "SKF Archive";
	ext            = [".skf"];
	forbidExtMatch = true;
	magic          = ["Archive: SKF"];
	weakMagic      = true;
	converters     = ["foremost"];
	notes          = "Don't have an extractor for this, but the samples I have often just have BMP and PNG files in them, so foremost handles this. NOTE: It should be pretty easy to reverse engineer this format, it looks very simple";
}
