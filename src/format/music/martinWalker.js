import {xu} from "xu";
import {Format} from "../../Format.js";

export class martinWalker extends Format
{
	name         = "Martin Walker Module";
	ext          = [".avp"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:MartinWalker]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
