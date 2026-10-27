import {Format} from "../../Format.js";

export class appleIIgsSampledInstrument extends Format
{
	name       = "Apple IIgs Sampled Instrument";
	magic      = ["Apple IIgs Sampled Instrument File"];
	converters = ["vibe2wav[renameOut]"];
}
