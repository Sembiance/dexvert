import {Format} from "../../Format.js";

export class wallyBeben extends Format
{
	name         = "Wall Beben Module";
	ext          = [".wb"];
	magic        = ["Wall Beben module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
