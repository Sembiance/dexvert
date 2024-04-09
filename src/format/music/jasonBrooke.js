import {xu} from "xu";
import {Format} from "../../Format.js";

export class jasonBrooke extends Format
{
	name         = "Jason Brooke";
	ext          = [".jb"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:JasonBrooke]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;	// due to being an extension only match
}
