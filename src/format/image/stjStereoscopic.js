import {Format} from "../../Format.js";

export class stjStereoscopic extends Format
{
	name       = "STJ Sterescopic Image";
	website    = "https://stereo.jpn.org/eng/stphmkr/";
	ext        = [".stj"];
	magic      = ["STJ Stereoscopic bitmap"];
	converters = ["konvertor"];
}
