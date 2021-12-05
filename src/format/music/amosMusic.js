import {Format} from "../../Format.js";

export class amosMusic extends Format
{
	name         = "AMOS Music Bank";
	website      = "http://fileformats.archiveteam.org/wiki/AMOS_Music_Bank";
	ext          = [".abk"];
	magic        = ["AMOS Music Bank", /^AMOS Basic memory bank.* type Music$/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
