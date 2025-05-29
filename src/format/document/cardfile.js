import {Format} from "../../Format.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class cardfile extends Format
{
	name           = "Cardfile Document";
	website        = "http://fileformats.archiveteam.org/wiki/Cardfile";
	ext            = [".crd"];
	magic          = ["Windows Cardfile database", "Cardfile", "deark: cardfile (CardFile", /^fmt\/1254( |$)/];
	forbiddenMagic = TEXT_MAGIC_STRONG;
	converters     = ["deark[module:cardfile] & cardfile"];
}
