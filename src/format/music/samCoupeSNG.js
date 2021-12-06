import {Format} from "../../Format.js";

export class samCoupeSNG extends Format
{
	name         = "Sam Coupe SNG Module";
	ext          = [".sng"];
	notes        = "Not all files converted, such as tetris.sng and shanhai.sng";
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
