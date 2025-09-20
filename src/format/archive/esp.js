import {Format} from "../../Format.js";

export class esp extends Format
{
	name           = "ESP Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ESP_(compressed_archive)";
	ext            = [".esp"];
	forbidExtMatch = true;
	magic          = ["ESP - Extension Sort Packer compressed archive", "ESP Archiv gefunden"];
	converters     = ["unesp"];
}
