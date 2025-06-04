import {Format} from "../../Format.js";

export class cryoVideo extends Format
{
	name         = "Cryo HNM/UBB Video";
	website      = "https://wiki.multimedia.cx/index.php/HNM";
	ext          = [".hnm", ".hns"];
	magic        = [/^CRYO HNM\d video$/, "CRYO UBB video", "Cryo HNM v4 (hnm)"];
	notes        = "FFMPEG has support for HNM4 but not other versions. Don't currently have a sample of HNM4. So the current samples DO NOT convert, but in the future with HNM4, it should.";
	metaProvider = ["mplayer"];
	converters   = ["na_game_tool[format:hnm4]", "na_game_tool[format:hnm1]", "na_game_tool[format:hnm40", "ffmpeg[format:hnm]"];
}
