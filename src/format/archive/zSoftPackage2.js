import {Format} from "../../Format.js";

export class zSoftPackage2 extends Format
{
	name           = "ZSoft Package 2";
	ext            = ["$"];
	forbidExtMatch = true;
	magic          = ["ZSoft Package format 2", "deark: zpk2"];
	converters     = ["deark[module:zpk2]"];
}
