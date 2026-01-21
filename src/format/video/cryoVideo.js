import {Format} from "../../Format.js";

export class cryoVideo extends Format
{
	name         = "Cryo HNM/UBB Video";
	website      = "https://wiki.multimedia.cx/index.php/HNM";
	ext          = [".hnm", ".hns"];
	magic        = [/^CRYO HNM\d video$/, "CRYO UBB video", "Cryo HNM v4 (hnm)", "Format: HNM"];
	notes        = "FFMPEG has support for HNM4 but not other versions. Don't currently have a sample of HNM4. So the current samples DO NOT convert, but in the future with HNM4, it should.";
	metaProvider = ["mplayer"];
	converters   = [
		"na_game_tool",	// lots of formats available, hnm0, hnm1, hnm4, hnm5, hnm6  Let's just let na_game_tool pick the right one
		"ffmpeg[format:hnm]"
	];
}
