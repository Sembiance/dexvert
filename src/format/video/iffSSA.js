import {Format} from "../../Format.js";

export class iffSSA extends Format
{
	name           = "ClariSSA Super Smooth Animation";
	website        = "http://fileformats.archiveteam.org/wiki/IFF-SSA";
	ext            = [".ssa", ".anim", ".ssad"];
	forbidExtMatch = true;
	magic          = ["IFF data, SSA super smooth animation", "ClariSSA Super Smooth Animation", "IFF SSAd file", "Generic IFF FORM file SSA5"];
	converters     = ["vibe2avi"];
	notes          = "Vibe coded converter still has many artifacts and issues, but it's better than nothing at all.";
}
