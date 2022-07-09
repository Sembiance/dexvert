import {Format} from "../../Format.js";

export class actionamics extends Format
{
	name         = "Actionamics Sound Tool Module";
	website      = "http://fileformats.archiveteam.org/wiki/Actionamics_Sound_Tool";
	ext          = [".ast"];
	magic        = ["Actionamics Sound Tool module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}

