import {Format} from "../../Format.js";

export class seuckFont extends Format
{
	name       = "Shoot Em Up Construction Kit Font";
	ext        = [".g"];
	fileSize   = 514;
	notes      = "Only one file format has been located. To prevent false positives it assumes this format is 514 bytes long, always.";
	converters = ["recoil2png"];
}
