import {Format} from "../../Format.js";

export class markII extends Format
{
	name         = "Mark II Sound-System Module";
	ext          = [".mk2", ".mkii"];
	magic        = ["Mark II Sound-System module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
