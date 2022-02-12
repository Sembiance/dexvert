import {Format} from "../../Format.js";

export class sngPlayer extends Format
{
	name         = "Reality AdLib Tracker";
	ext          = [".sng"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
