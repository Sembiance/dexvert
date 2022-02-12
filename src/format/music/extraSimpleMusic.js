import {Format} from "../../Format.js";

export class extraSimpleMusic extends Format
{
	name         = "eXtra Simple Music";
	ext          = [".xsm"];
	magic        = ["eXtra Simple Music", "Extra Simple Music module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
