import {Format} from "../../Format.js";

export class nistSphere extends Format
{
	name         = "NIST Sphere Audio";
	ext          = [".sd"];
	magic        = ["NIST SPHERE file", "NIST Sphere waveform audio"];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
