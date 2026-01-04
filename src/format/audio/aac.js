import {Format} from "../../Format.js";

export class aac extends Format
{
	name           = "Advanced Audio Coding";
	website        = "http://fileformats.archiveteam.org/wiki/AAC";
	ext            = [".aac", ".m4a", ".mp4", ".ima"];
	forbidExtMatch = [".ima"];
	magic          = ["MPEG-4 LC-AAC Audio", "MPEG ADTS, AAC", "MPEG-2 LC-AAC Audio", "AAC Audio", "ISO Media, Apple iTunes ALAC/AAC-LC", "audio/aac", "audio/mp4", "raw ADTS AAC (Advanced Audio Coding) (aac)"];
	idMeta         = ({macFileType}) => macFileType==="M4A ";
	metaProvider   = ["soxi"];
	converters     = ["sox", "ffmpeg[outType:mp3]"];	// no types for sox or ffmpeg because the input file type can vary
}
