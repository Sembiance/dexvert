import {Format} from "../../Format.js";

export class pet extends Format
{
	name       = "PETSCII Editor";
	ext        = [".pet"];
	fileSize   = 2026;
	converters = ["recoil2png"];
}
