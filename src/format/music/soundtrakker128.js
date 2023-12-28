import {Format} from "../../Format.js";

export class soundtrakker128 extends Format
{
	name           = "Soundtrakker 128";
	website        = "http://fileformats.archiveteam.org/wiki/Soundtrakker_128_module";
	ext            = [".128"];
	magic          = ["Soundtrakker 128"];
	unsupported    = true;
	notes          = "No known converter. The sample files identify as Soundtrakker 128, but not sure if they really are or not.";
}
