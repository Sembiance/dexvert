import {xu} from "xu";
import {Format} from "../../Format.js";

export class desireModule extends Format
{
	name         = "Desire Module";
	ext          = [".dsr"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:Desire]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
