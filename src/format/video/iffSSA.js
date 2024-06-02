import {Format} from "../../Format.js";

export class iffSSA extends Format
{
	name        = "ClariSSA Super Smooth Animation";
	website     = "http://fileformats.archiveteam.org/wiki/IFF-SSA";
	ext         = [".ssa", ".anim", ".ssad"];
	magic       = ["IFF data, SSA super smooth animation", "ClariSSA Super Smooth Animation", "IFF SSAd file"];
	unsupported = true;
	notes       = "Couldn't find any working modern converter that works on any of the sample files.";
}
