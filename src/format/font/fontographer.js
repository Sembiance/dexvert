import {Format} from "../../Format.js";

export class fontographer extends Format
{
	name        = "Fontographer";
	website     = "http://fileformats.archiveteam.org/wiki/Fontographer";
	ext         = [".fog"];
	magic       = ["Fontographer Font"];
	converters  = ["fontographer"];
	notes       = "The Fontographer program is CRAZY sensitive to register. It was working, but a 86Box update changed hardware and Fontographer no longer registers. Meh, only 533 unique files have been found on discmaster, so just disable support for this";
	unsupported = true;
}
