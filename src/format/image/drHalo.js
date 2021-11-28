import {Format} from "../../Format.js";

export class drHalo extends Format
{
	name          = "Dr. Halo";
	website       = "http://fileformats.archiveteam.org/wiki/Dr._Halo";
	ext           = [".cut", ".pal", ".pic"];
	mimeType      = "application/dr-halo";
	priority      = this.PRIORITY.LOW;
	converters    = ["convert", "recoil2png", `abydosconvert[format:${this.mimeType}]`]
	metaProvider = ["image"];

	// Due to not having a good magic, we reject any created images less than 2 colors
	verify = ({meta}) => meta.colorCount>1;
}
