import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class nokiaLogoManager extends Format
{
	name           = "Nokia Logo Manager bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Nokia_Logo_Manager_bitmap";
	ext            = [".nlm"];
	magic          = ["Nokia Logo Manager bitmap"];
	forbiddenMagic = TEXT_MAGIC_STRONG;
	converters     = ["deark", "nconvert"];
}
