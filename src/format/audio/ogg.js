import {Format} from "../../Format.js";

export class ogg extends Format
{
	name         = "Ogg Vorbis Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Ogg";
	ext          = [".ogg", ".oga"];
	magic        = ["OGG Vorbis audio", "Ogg data, Vorbis audio", "audio/x-vorbis+ogg", "deark: ogg (Ogg ", /^soxi: vorbis$/, /^fmt\/203( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="Ogg!" && macFileCreator==="Nox!";
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
