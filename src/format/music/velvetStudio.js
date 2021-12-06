import {Format} from "../../Format.js";

export class velvetStudio extends Format
{
	name         = "Velvet Studio Module";
	website      = "http://fileformats.archiveteam.org/wiki/Velvet_Studio";
	ext          = [".ams"];
	magic        = ["Velvet Studio AMS Module", "Velvet Studio Advanced Module System module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "openmpt123"];
}
