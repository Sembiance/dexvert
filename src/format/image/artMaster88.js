import {Format} from "../../Format.js";

export class artMaster88 extends Format
{
	name       = "ArtMaster88";
	website    = "http://fileformats.archiveteam.org/wiki/ArtMaster88";
	ext        = [".img"];
	magic      = ["ArtMaster88"];
	mimeType   = "image/x-artmaster";
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
