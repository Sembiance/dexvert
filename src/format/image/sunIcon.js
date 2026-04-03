import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class sunIcon extends Format
{
	name           = "Sun Icon/Cursor";
	website        = "http://fileformats.archiveteam.org/wiki/Sun_icon";
	ext            = [".ico", ".icon", ".cursor", ".pr", ".image", ".im", ".cicon", ".h"];
	forbidExtMatch = true;
	magic          = ["Sun Icon/Cursor :icon:", ...TEXT_MAGIC];
	weakMagic      = TEXT_MAGIC;
	notes          = "Color currently isn't supported. Don't know of a converter that supports it due to palettes not being embedded within the file.";
	converters     = ["nconvert[format:icon]", "imconv[format:icon]"];
}
