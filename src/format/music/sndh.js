import {Format} from "../../Format.js";

export class sndh extends Format
{
	name           = "SNDH Module";
	website        = "http://fileformats.archiveteam.org/wiki/Atari_SoundHeader";
	ext            = [".sndh", ".snd"];
	forbidExtMatch = [".snd"];
	magic          = ["SNDH Atari ST music SNDH Atari ST music", "SNDH Atari ST music", "Atari SoundHeader music"];
	converters     = ["sndh2raw"];
	post           = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="sndh2raw")?.meta || {});
}
