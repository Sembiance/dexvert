import {Format} from "../../Format.js";

export class gfaArtist extends Format
{
	name       = "GFA Artist";
	website    = "http://fileformats.archiveteam.org/wiki/GFA_Artist";
	ext        = [".art"];
	mimeType   = "image/x-gfa-artist";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
