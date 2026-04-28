import {Format} from "../../Format.js";

export class soundtrakker128 extends Format
{
	name        = "Soundtrakker 128";
	website     = "http://fileformats.archiveteam.org/wiki/Soundtrakker_128_module";
	ext         = [".128", ".st2"];
	magic       = ["SoundTrakker128 tune", /^Soundtrakker 128/];
	weakMagic   = [/^Soundtrakker 128/];	// might be ok to remove this from weakMagic IF I have a valid converter
	unsupported = true;	// only 47 unique files on discmaster
}
