import {Format} from "../../Format.js";

export class sc68 extends Format
{
	name        = "sc68 Atari ST Music";
	website     = "http://fileformats.archiveteam.org/wiki/SC68";
	ext         = [".sc68"];
	magic       = ["sc68 Atari ST music", "sc68 soundchip music"];
	converters = ["sndh2raw"];
	post       = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="sndh2raw").meta);
}
