import {Format} from "../../Format.js";

export class deluxeVideo extends Format
{
	name        = "Deluxe Video";
	website     = "http://fileformats.archiveteam.org/wiki/VDEO";
	magic       = ["Deluxe Video III video", "Deluxe Video project", "Generic IFF FORM file VDEO"];
	unsupported = true;	// These are VERY small files, so I have a strong hunch that these are actually just "project" files and no actual video or animation is within them
	notes       = "Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.";
}
