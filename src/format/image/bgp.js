import {Format} from "../../Format.js";

export class bgp extends Format
{
	name       = "Bugbiter APAC239i";
	website    = "http://fileformats.archiveteam.org/wiki/Bugbiter_APAC239i";
	ext        = [".bgp"];
	magic      = ["Bugbiter APAC239i bitmap"];
	converters = ["recoil2png"];
}
