import {Format} from "../../Format.js";

export class idRoQ extends Format
{
	name         = "Id Software RoQ Video";
	website      = "https://wiki.thedarkmod.com/index.php?title=Playing_ROQ_Video_Files";
	ext          = [".roq"];
	magic        = ["Id Software RoQ video", "id RoQ (roq)"];
	metaProvider = ["mplayer"];
	converters   = ["na_game_tool[format:roq]", "ffmpeg[format:roq]"];
}
