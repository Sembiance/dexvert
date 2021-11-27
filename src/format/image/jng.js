import {Format} from "../../Format.js";

export class jng extends Format
{
	name       = "JPEG Network Graphics";
	website    = "http://fileformats.archiveteam.org/wiki/JNG";
	ext        = [".jng"];
	mimeType   = "image/x-jng";
	magic      = ["JPEG Network Graphics", "JNG video data"];
	converters = ["convert", "nconvert", `abydosconvert[format:${this.mimeType}]`]
	metaProviders = ["image"];
}
