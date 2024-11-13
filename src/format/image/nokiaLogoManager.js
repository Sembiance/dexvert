import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class nokiaLogoManager extends Format
{
	name           = "Nokia Logo Manager bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Nokia_Logo_Manager_bitmap";
	ext            = [".nlm"];
	magic          = ["Nokia Logo Manager bitmap"];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["deark[module:nlm][matchType:magic]", "nconvert", "wuimg[matchType:magic]"];
}
