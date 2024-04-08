import {Format} from "../../Format.js";

export class daveLoweModule extends Format
{
	name         = "Dave Lowe Module";
	ext          = [".dl"];
	magic        = ["Dave Lowe module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
