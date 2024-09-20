import {Format} from "../../Format.js";

export class aac extends Format
{
	name           = "Advanced Audio Coding";
	website        = "http://fileformats.archiveteam.org/wiki/AAC";
	ext            = [".aac", ".m4a", ".mp4", ".ima"];
	forbidExtMatch = [".ima"];
	magic          = ["MPEG-4 LC-AAC Audio", "MPEG ADTS, AAC", "MPEG-2 LC-AAC Audio", "AAC Audio", "ISO Media, Apple iTunes ALAC/AAC-LC", "audio/aac", "audio/mp4"];
	metaProvider   = ["soxi"];
	converters     = ["sox", "ffmpeg[outType:mp3]"];
}
