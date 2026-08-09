import {Format} from "../../Format.js";

export class travellersTalesFMV extends Format
{
	name           = "Traveller's Tales FMV Video";
	ext            = [".fmv"];
	forbidExtMatch = true;
	magic          = ["Traveller's Tales FMV (ttfmv)"];
	converters     = ["ffmpeg[libre][format:ttfmv]"];
}
