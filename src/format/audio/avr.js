import {Format} from "../../Format.js";

export class avr extends Format
{
	name         = "Audio Visual Research";
	website      = "http://fileformats.archiveteam.org/wiki/AVR";
	ext          = [".avr"];
	magic        = [/^Audio Visual Research (file|sample)/, "AVR (Audio Visual Research) (avr)", /^soxi: avr$/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
