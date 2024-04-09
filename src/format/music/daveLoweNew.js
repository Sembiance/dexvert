import {xu} from "xu";
import {Format} from "../../Format.js";

export class daveLoweNew extends Format
{
	name         = "Dave Lowe New Module";
	ext          = [".dln"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:DaveLoweNew]"];
	verify       = ({meta}) => meta.duration>=(xu.SECOND*3);
}
