import {Format} from "../../Format.js";

export class sonyOpenMG extends Format
{
	name           = "Sony OpenMG Audio";
	ext            = [".aa3"];
	forbidExtMatch = true;
	magic          = ["ATRAC3 encoded audio", "Sony OpenMG audio (oma)"];
	converters     = ["ffmpeg[format:oma][outType:mp3]"];
}
