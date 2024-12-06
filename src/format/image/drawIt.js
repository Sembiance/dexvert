import {Format} from "../../Format.js";

export class drawIt extends Format
{
	name          = "DrawIt";
	website       = "http://fileformats.archiveteam.org/wiki/DrawIt_(Atari)";
	ext           = [".dit"];
	fileSize      = 3845;
	matchFileSize = true;
	fallback      = true;
	converters    = ["recoil2png"];
	unsupported   = true;
	notes         = "Can only match based on fileSize and recoil2png converts most garbage into a garbage image. Only encountered about 6 of these in all of discmaster2, but false positives are around 1,000 which is too high a ratio to bother supporting.";
}
