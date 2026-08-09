import {Format} from "../../Format.js";

export class rpzaVideo extends Format
{
	name           = "RPZA Video";
	ext            = [".pdv"];
	forbidExtMatch = true;
	magic          = ["RPZA Video (rpza)"];
	converters     = ["ffmpeg[libre][format:rpza]"];
}
