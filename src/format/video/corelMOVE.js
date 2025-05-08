import {Format} from "../../Format.js";

export class corelMOVE extends Format
{
	name         = "CorelMOVE Animation";
	website      = "http://fileformats.archiveteam.org/wiki/CorelMOVE";
	ext          = [".cmv"];
	magic        = ["Corel Move animation", "RIFF Datei: unbekannter Typ 'cmov'", "Generic RIFF file cmov"];
	converters   = ["corelMOVE"];
}
