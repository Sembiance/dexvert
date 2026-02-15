import {Format} from "../../Format.js";

export class artMaster88 extends Format
{
	name           = "ArtMaster88";
	website        = "http://fileformats.archiveteam.org/wiki/ArtMaster88";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["ArtMaster88"];
	mimeType       = "image/x-artmaster";
	converters     = ["recoil2png[format:IMG.ArtMaster88,ARV]", `abydosconvert[format:${this.mimeType}]`];
}
