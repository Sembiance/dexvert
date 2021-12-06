import {Format} from "../../Format.js";

export class megatracker extends Format
{
	name         = "Megatracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Megatracker_module";
	ext          = [".mgt"];
	magic        = ["Megatracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
