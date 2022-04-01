import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaASF extends Format
{
	name           = "Electronic Arts ASF";
	ext            = [".asf"];
	forbidExtMatch = true;
	magic          = ["Electronic Arts ASF video"];
	converters     = ["vgmstream"];
	verify         = ({meta}) => meta.duration>=(xu.SECOND*2);
}
