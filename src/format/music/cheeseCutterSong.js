import {Format} from "../../Format.js";

export class cheeseCutterSong extends Format
{
	name        = "Cheese Cutter Song";
	ext         = [".ct"];
	magic       = ["CheeseCutter 2 song"];
	unsupported = true;
	notes       = "Player here https://github.com/theyamo/CheeseCutter requires D compiler gdc to build (https://wiki.gentoo.org/wiki/Dlang) but player doesn't seem to convert CLI conversion anyways";
}
