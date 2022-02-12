import {Format} from "../../Format.js";

export class deFyTracker extends Format
{
	name         = "DeFy Tracker";
	ext          = [".dtm"];
	magic        = ["DeFy Tracker Module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
