import {Format} from "../../Format.js";

export class bink extends Format
{
	name           = "Bink Video";
	website        = "http://fileformats.archiveteam.org/wiki/Bink_Video";
	ext            = [".bik", ".bik2", ".bk2"];
	forbidExtMatch = true;
	magic          = [/^Bink2? [Vv]ideo/, "video/vnd.radgamettools.bink", "Bink (bink)", "Format: BIK", /^fmt\/731( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="BINK" && macFileCreator==="BINK";
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg"];	// nihav has messed up audio for most bink files and ffmpeg seems to handle all the ones I've found
}
