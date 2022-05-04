import {Format} from "../../Format.js";

export class smacker extends Format
{
	name         = "Smacker Video";
	website      = "http://fileformats.archiveteam.org/wiki/Smacker";
	ext          = [".smk"];
	magic        = ["Smacker movie/video (original)", "Smacker Video", /^RAD Game Tools Smacker Multimedia .* frames$/, /^fmt\/1234( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:smk]"];
}
