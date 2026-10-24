import {Format} from "../../Format.js";

export class saturnSAP extends Format
{
	name           = "Saturn SAP Audio";
	ext            = [".sap"];
	forbidExtMatch = true;
	magic          = ["Saturn SAP (satsap)", "vgmstream: sat_sap"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:satsap][outType:mp3]", "vgmstream[types:sat_sap]"];
}
