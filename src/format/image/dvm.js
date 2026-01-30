import {Format} from "../../Format.js";

export class dvm extends Format
{
	name           = "Magic Software DVM";
	website        = "http://fileformats.archiveteam.org/wiki/DVM";
	ext            = [".dvm"];
	forbidExtMatch = true;
	magic          = ["DVM video"];
	converters     = ["wuimg[format:dvm] -> *ffmpeg[fps:15][outType:gif]"];
}
