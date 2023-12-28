import {Format} from "../../Format.js";

export class soundMon extends Format
{
	name         = "Brian Postma SoundMon module";
	website      = "http://fileformats.archiveteam.org/wiki/Brian_Postma_SoundMon_v2.x_&_v3.x_module";
	ext          = [".bp", ".bp3"];
	magic        = [/^BP SoundMon [123] module$/];
	notes        = "Not all files convert properly, such as CYBERSONG and SANXION";
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:SoundMon2.0]", "uade123[player:SoundMon2.2]"];
}
