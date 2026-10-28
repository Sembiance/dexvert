import {Format} from "../../Format.js";

export class hyperStudioSampledSound extends Format
{
	name       = "HyperStudio sampled sound";
	magic      = ["HyperStudio sampled sound"];
	converters = ["vibe2wav[renameOut]"];
}
