import {Format} from "../../Format.js";

export class smacker extends Format
{
	name         = "Smacker Video";
	website      = "http://fileformats.archiveteam.org/wiki/Smacker";
	ext          = [".smk"];
	magic        = ["Smacker movie/video", "Smacker Video", "video/vnd.radgamettools.smacker", "Smacker (smk)", "Format: Smacker Video", /^RAD Game Tools Smacker Multimedia .* frames$/, /^fmt\/1234( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="DDat" && macFileCreator==="DLCK";
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:smk]"];
}
