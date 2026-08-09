import {Format} from "../../Format.js";

export class cyberflixDreamFactory5 extends Format
{
	name           = "Cyberflix DreamFactory 5 Video";
	ext            = [".move"];
	forbidExtMatch = true;
	magic          = ["CFDF D5 (Cyberflix DreamFactory v5) (cfdf_d5)"];
	converters     = ["ffmpeg[libre][format:cfdf_d5]"];
}
