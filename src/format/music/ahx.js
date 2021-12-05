import {Format} from "../../Format.js";

export class ahx extends Format
{
	name         = "Abyss Highest Experience Module";
	website      = "http://fileformats.archiveteam.org/wiki/AHX_(Abyss)";
	ext          = [".ahx"];
	magic        = [/^AHX .*module data/, "Abyss' Highest eXperience module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "zxtune123"];
}
