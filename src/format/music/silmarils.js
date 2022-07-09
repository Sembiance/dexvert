import {Format} from "../../Format.js";

export class silmarils extends Format
{
	name         = "Silmarils Module";
	website      = "http://fileformats.archiveteam.org/wiki/Silmarils";
	ext          = [".mok"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Silmarils]"];
}
