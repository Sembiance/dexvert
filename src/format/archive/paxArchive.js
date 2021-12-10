import {Format} from "../../Format.js";

export class paxArchive extends Format
{
	name        = "Pax Archive";
	ext         = [".pax"];
	magic       = ["Pax compressed archive"];
	unsupported = true;
	notes       = "Used in Atari ST program GEM-View";
}
