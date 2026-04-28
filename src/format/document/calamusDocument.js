import {Format} from "../../Format.js";

export class calamusDocument extends Format
{
	name        = "Calamus Document";
	website     = "http://fileformats.archiveteam.org/wiki/Calamus";
	ext         = [".cdk"];
	magic       = ["Calamus Document"];
	unsupported = true;	// 1,1122 unique files on discmaster, but it's a complicated format including fonts, vector graphics and more. abandoned vibe coder attempts in legacy/vibe/calamusDocument*
}
