import {Format} from "../../Format.js";

export class gfaArtist extends Format
{
	name       = "GFA Artist";
	website    = "http://fileformats.archiveteam.org/wiki/GFA_Artist";
	ext        = [".art"];
	mimeType   = "image/x-gfa-artist";
	converters = ["recoil2png[format:ART.GfaArtist]", `abydosconvert[format:${this.mimeType}]`];
}
