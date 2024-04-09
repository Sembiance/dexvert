import {Format} from "../../Format.js";

export class soundFactory extends Format
{
	name         = "SoundFactory Module";
	website      = "http://fileformats.archiveteam.org/wiki/Soundfactory";
	ext          = [".psf"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:SoundFactory]"];
}
