import {Format} from "../../Format.js";

export class sndh extends Format
{
	name        = "SNDH Module";
	website     = "http://fileformats.archiveteam.org/wiki/SNDH";
	ext         = [".sndh"];
	magic       = ["SNDH Atari ST music SNDH Atari ST music", "SNDH Atari ST music", "Atari SoundHeader music"];
	unsupported = true;
	notes       = "Lots of Atari based converters at the website";
}
