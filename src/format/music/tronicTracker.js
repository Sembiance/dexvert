import {xu} from "xu";
import {Format} from "../../Format.js";

export class tronicTracker extends Format
{
	name         = "Tronic Tracker";
	ext          = [".tronic"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Tronic]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
