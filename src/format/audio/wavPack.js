import {Format} from "../../Format.js";

export class wavPack extends Format
{
	name         = "WavPack";
	website      = "http://fileformats.archiveteam.org/wiki/WavPack";
	ext          = [".wv", ".wvc"];
	magic        = ["WavPack Lossless Audio", "WavPack compressed audio correction data"];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
