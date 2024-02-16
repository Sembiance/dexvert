import {Format} from "../../Format.js";

export class installIt extends Format
{
	name       = "InstallIt! Compressed File";
	website    = "http://justsolve.archiveteam.org/wiki/InstallIt!";
	ext        = ["_"];
	magic      = ["InstallIt! compressed file"];
	converters = ["installIt"];
}
