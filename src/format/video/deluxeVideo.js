import {Format} from "../../Format.js";

export class deluxeVideo extends Format
{
	name        = "Deluxe Video";
	website     = "http://fileformats.archiveteam.org/wiki/VDEO";
	magic       = ["Deluxe Video III video", "Deluxe Video project", "Generic IFF FORM file VDEO"];
	unsupported = true;
	notes       = "Couldn't find a converter for it. Could fire up an amiga with deluxe video program from Electronic Arts.";
}
