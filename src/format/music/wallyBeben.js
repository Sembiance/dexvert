import {Format} from "../../Format.js";

export class wallyBeben extends Format
{
	name         = "Wally Beben Module";
	ext          = [".wb"];
	magic        = ["Wally Beben module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
