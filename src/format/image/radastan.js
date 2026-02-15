import {Format} from "../../Format.js";

export class radastan extends Format
{
	name       = "ZX-Uno Radastan";
	ext        = [".rad"];
	fileSize   = 6160;
	converters = ["recoil2png[format:RAD]"];
}
