import {Format} from "../../Format.js";

export class silmarils extends Format
{
	name         = "Silmarils Module";
	ext          = [".mok"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Silmarils]"];
}
