import {xu} from "xu";
import {Format} from "../../Format.js";

export class audiokineticWWISE extends Format
{
	name       = "Audiokinetic WWISE Audio";
	ext        = [".wem"];
	magic      = ["Audiokinetic WWISE Audio", "vgmstream: wwise"];
	converters = ["vgmstream[types:wwise]"];
}
