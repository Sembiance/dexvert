import {Format} from "../../Format.js";

export class paradoxDatabase extends Format
{
	name           = "Paradox Database Table";
	website        = "http://fileformats.archiveteam.org/wiki/Paradox_(database)";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = [/^fmt\/(350|351|352)( |$)/];
	converters     = ["pxview"];
}
