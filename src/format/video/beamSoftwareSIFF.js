import {Format} from "../../Format.js";

export class beamSoftwareSIFF extends Format
{
	name         = "Beam Software SIFF Video";
	website      = "https://wiki.multimedia.cx/index.php/SIFF";
	ext          = [".vb", ".vbc"];
	magic        = ["Beam Software SIFF video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
