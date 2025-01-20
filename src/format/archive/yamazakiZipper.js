import {Format} from "../../Format.js";

export class yamazakiZipper extends Format
{
	name           = "Yamazaki zipper Archive";
	website        = "http://justsolve.archiveteam.org/wiki/Yamazaki_zipper_archive";
	ext            = [".yz1"];
	forbidExtMatch = true;
	magic          = ["Yamazaki Zipper compressed archive", /^DeepFreezer archive data/];
	converters     = ["deepFreezer"];
}
