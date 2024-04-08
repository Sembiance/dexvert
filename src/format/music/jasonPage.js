import {Format} from "../../Format.js";

export class jasonPage extends Format
{
	name         = "Jason Page/Steve Turner Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Jason_Page";
	ext          = [".jpo", ".jpn"];
	magic        = ["Jason Page audio format"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:JasonPage]", "uade123[player:SteveTurner]"];
}
