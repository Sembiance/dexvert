import {Format} from "../../Format.js";

export class doodleC64 extends Format
{
	name           = "Doodle C64";
	website        = "http://fileformats.archiveteam.org/wiki/Doodle!_(C64)";
	ext            = [".dd", ".jj"];
	magic          = ["Doodle bitmap (compressed)", "Doodle C64"];
	priority       = this.PRIORITY.LOW;
	fileSize       = {".dd" : [9218, 9026, 9346]};
	matchFileSize  = true;
	converters     = ["recoil2png[format:JJ,DD]", "nconvert[matchType:magic]"];
}
