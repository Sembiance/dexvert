import {Format} from "../../Format.js";

export class ircam extends Format
{
	name         = "IRCAM Sound Format";
	website      = "http://fileformats.archiveteam.org/wiki/Berkeley/IRCAM/Carl_Sound_Format";
	ext          = [".sf"];
	magic        = ["IRCAM file", "IRCAM Sound Format audio", "Berkeley/IRCAM/CARL Sound Format (ircam)", /^soxi: sf$/];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
