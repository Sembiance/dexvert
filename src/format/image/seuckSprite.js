import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class seuckSprite extends Format
{
	name           = "Shoot 'Em Up Construction Kit Sprite";
	website        = "http://fileformats.archiveteam.org/wiki/Shoot_%27Em_Up_Construction_Kit";
	ext            = [".a"];
	safeExt        = ".a";
	fileSize       = 8130;
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png"];
}
