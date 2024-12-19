import {Format} from "../../Format.js";

export class freeMotionFlashMovie extends Format
{
	name           = "FreeMotion Flash Movie";
	ext            = [".sqf"];
	forbidExtMatch = true;
	magic          = ["FreeMotion Flash movie"];
	weakMagic      = true;
	converters     = ["foremost"];
}
