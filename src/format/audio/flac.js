import {Format} from "../../Format.js";

export class flac extends Format
{
	name         = "Free Lossless Audio Codece";
	website      = "http://fileformats.archiveteam.org/wiki/FLAC";
	ext          = [".flac"];
	mimeType     = "audio/x-flac";
	magic        = ["FLAC audio bitstream data", "FLAC lossless compressed audio", "FLAC (Free Lossless Audio Codec)", "FLAC audio data", "audio/flac", /^fmt\/279( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox"];
}
