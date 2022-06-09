import {Format} from "../../Format.js";

export class photoCDAudio extends Format
{
	name           = "PhotoCD Audio";
	ext            = [".pcd"];
	forbidExtMatch = true;
	filename       = [/^audio\d+\.pcd$/i];
	converters     = ["sox[type:raw][rate:44100][channels:2][bits:16][encoding:signed-integer]", "sox[type:cdda]"];
	notes          = "Some files are CDDA (audio06.pcd) but others are some sort of raw, which default to above (audio54.pcd)";
}
