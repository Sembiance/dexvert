import {Format} from "../../Format.js";

export class jpegLS extends Format
{
	name       = "JPEG-LS";
	website    = "http://fileformats.archiveteam.org/wiki/JPEG-LS";
	ext        = [".jls"];
	magic      = ["JPEG-LS bitmap", /^JPEG-LS image data/, "piped jpegls sequence (jpegls_pipe)"];
	converters = ["wuimg[format:jpegls]", "ffmpeg[format:jpegls_pipe][outType:png]"];
}
