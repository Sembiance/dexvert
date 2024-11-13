import {Format} from "../../Format.js";

export class smush extends Format
{
	name         = "LucasArts SMUSH Video";
	website      = "https://wiki.multimedia.cx/index.php/Smush";
	ext          = [".nut", ".san"];
	magic        = ["LucasArts Smush Animation Format", "Smush Animation format", "LucasArts Smush (smush)", "LucasArts Smush v2 (SANM) video"];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="SMSH" && macFileCreator==="LApl";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:smush]"];
}
