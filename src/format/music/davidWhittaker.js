import {xu} from "xu";
import {Format} from "../../Format.js";

export class davidWhittaker extends Format
{
	name         = "David Whittaker";
	website      = "http://fileformats.archiveteam.org/wiki/David_Whittaker";
	ext          = [".dw"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:DavidWhittaker]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;	// due to being an extension only match
}
