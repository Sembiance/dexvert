import {Format} from "../../Format.js";

export class dvm extends Format
{
	name           = "DVM";
	website        = "http://fileformats.archiveteam.org/wiki/DVM";
	ext            = [".dvm"];
	forbidExtMatch = true;
	magic          = ["DVM video"];
	converters     = ["wuimg -> *ffmpeg[fps:15][outType:gif]"];
}
