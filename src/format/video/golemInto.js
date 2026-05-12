import {Format} from "../../Format.js";

export class golemInto extends Format
{
	name       = "Golem Into Video";
	ext        = [".xfl"];
	converters = ["na_eofdec[format:golem-xfl]"];
	unsupported = true; // No good way to identify them, other than extension, which would work, but the samples I tried with na_eofdec just produced black video with static sound, so pass on this format for now
}
