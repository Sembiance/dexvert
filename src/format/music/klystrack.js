import {Format} from "../../Format.js";

export class klystrack extends Format
{
	name        = "Klystrack Module";
	website     = "http://fileformats.archiveteam.org/wiki/Klystrack_module";
	ext         = [".kt"];
	magic       = ["Klystrack chiptune", "Klystrack song"];
	unsupported = true;
}
