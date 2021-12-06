import {Format} from "../../Format.js";

export class multiMediaSound extends Format
{
	name         = "MultiMedia Sound Module";
	ext          = [".mms"];
	magic        = ["MultiMedia Sound module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "zxtune123", "openmpt123"];
}
