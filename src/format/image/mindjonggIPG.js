import {Format} from "../../Format.js";

export class mindjonggIPG extends Format
{
	name       = "Mindjongg IPG";
	website    = "http://fileformats.archiveteam.org/wiki/Mindjongg_tileset";
	ext        = [".ipg"];
	magic      = ["Mindjongg :ipg:", "deark: mindjongg"];
	converters = ["deark[module:mindjongg]", "nconvert[extractAll][format:ipg]"];
}
