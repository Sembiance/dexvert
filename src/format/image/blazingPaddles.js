import {Format} from "../../Format.js";

export class blazingPaddles extends Format
{
	name          = "Blazing Paddles";
	website       = "http://fileformats.archiveteam.org/wiki/Blazing_Paddles";
	ext           = [".pi"];
	magic         = ["Blazing Paddles :pi:"];
	mimeType      = "image/x-blazing-paddles";
	fileSize      = [10240, 10242];
	matchFileSize = true;
	converters    = ["recoil2png[format:PI.Bpl]", "nconvert[format:pi]", "view64"];	// abydosconvert[format:${this.mimeType}] messes too much stuff up
	verify        = ({meta}) => meta.colorCount>1;
}
