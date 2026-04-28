import {Format} from "../../Format.js";

export class aProSys extends Format
{
	name        = "AProSys Module";
	website     = "http://fileformats.archiveteam.org/wiki/AProSys_module";
	ext         = [".amx", ".aps"];
	matchPreExt = true;
	magic       = ["AProSys module", /^AProSys⇥module$/];
	unsupported = true;	// only 30 unique files on discmaster, a vibe converter was started but abandoned see vibe/legacy/aProSys/
}
