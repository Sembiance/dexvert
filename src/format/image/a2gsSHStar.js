import {Format} from "../../Format.js";

export class a2gsSHStar extends Format
{
	name       = "Apple IIGS SH3/SHR";
	ext        = [".sh3", ".shr"];
	fileSize   = 38400;
	converters = ["recoil2png"];
	verify     = ({meta}) => meta.colorCount>1;
}
