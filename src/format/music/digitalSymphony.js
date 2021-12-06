import {Format} from "../../Format.js";

export class digitalSymphony extends Format
{
	name         = "Digital Symphony Module";
	website      = "http://fileformats.archiveteam.org/wiki/Digital_Symphony_module";
	ext          = [".dsym"];
	magic        = ["Digital Symphony relocatable module", "Digital Symphony song"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123"];
}
