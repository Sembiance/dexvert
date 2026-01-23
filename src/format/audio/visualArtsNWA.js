import {Format} from "../../Format.js";

export class visualArtsNWA extends Format
{
	name           = "Visual Arts NWA";
	ext            = [".nwa"];
	forbidExtMatch = true;
	magic          = ["Visual Arts NWA (nwa)"];
	weakMagic      = true;
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[outType:mp3][libre]"];
	verify         = ({soxiMeta}) => soxiMeta.duration>=100;
}
