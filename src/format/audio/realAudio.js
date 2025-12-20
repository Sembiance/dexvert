import {Format} from "../../Format.js";

export class realAudio extends Format
{
	name             = "RealAudio";
	website          = "http://fileformats.archiveteam.org/wiki/RealMedia";
	ext              = [".rm", ".ra", ".rma", ".rmf"];
	magic            = [/^RealMedia [Ff]ile/, "Real Media stream", "RealAudio", "Real Audio", "application/vnd.rn-realmedia", "RealMedia (rm)", /^soxi: ra$/, /^fmt\/404( |$)/, /^x-fmt\/(190|278)( |$)/];
	idMeta           = ({macFileType, macFileCreator}) => macFileType==="PNRA" && macFileCreator==="PNst";
	confidenceAdjust = () => -10;	// Reduce by 10 so that wmv matches first
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]"];
}
