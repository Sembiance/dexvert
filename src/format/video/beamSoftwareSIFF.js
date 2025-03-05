import {Format} from "../../Format.js";

export class beamSoftwareSIFF extends Format
{
	name         = "Beam Software SIFF Video";
	website      = "https://wiki.multimedia.cx/index.php/SIFF";
	ext          = [".vb", ".vbc"];
	magic        = ["Beam Software SIFF video", "Beam Software SIFF (siff)", /^fmt\/1559( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["na_game_tool[format:siff]", "ffmpeg[format:siff]"];
}
