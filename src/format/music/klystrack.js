import {Format} from "../../Format.js";

export class klystrack extends Format
{
	name           = "Klystrack Module";
	website        = "http://fileformats.archiveteam.org/wiki/Klystrack_module";
	ext            = [".kt"];
	forbidExtMatch = true;
	magic          = ["Klystrack chiptune", "Klystrack song"];
	unsupported    = true; // only 22 unique files on discmaster
}
