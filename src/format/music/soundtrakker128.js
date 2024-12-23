import {Format} from "../../Format.js";

export class soundtrakker128 extends Format
{
	name           = "Soundtrakker 128";
	website        = "http://fileformats.archiveteam.org/wiki/Soundtrakker_128_module";
	ext            = [".128", ".st2"];
	magic          = ["Soundtrakker 128", "SoundTrakker128 tune"];
	unsupported    = true;
	notes          = "No known converter. The sample files identify as Soundtrakker 128, but not sure if they really are or not.";
}
