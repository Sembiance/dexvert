import {xu} from "xu";
import {Format} from "../../Format.js";

export class coreDesign extends Format
{
	name         = "Core Design Module";
	ext          = [".core"];
	magic        = ["Core Design module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:CoreDesign]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
