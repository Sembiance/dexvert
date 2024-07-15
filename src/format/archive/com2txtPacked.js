import {Format} from "../../Format.js";

export class com2txtPacked extends Format
{
	name           = "COM2TXT Packed";
	website        = "http://fileformats.archiveteam.org/wiki/Com2txt";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["com2txt 16bit DOS executable"];
	packed         = true;
	converters     = ["com2txt"];
}
