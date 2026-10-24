import {Format} from "../../Format.js";

export class visualArtsNWA extends Format
{
	name           = "Visual Arts NWA";
	ext            = [".nwa"];
	forbidExtMatch = true;
	magic          = ["Visual Arts NWA (nwa)", "vgmstream: nwa"];
	weakMagic      = true;
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["vgmstream[types:nwa]", "ffmpeg[outType:mp3][format:nwa][libre]"];
	verify         = ({soxiMeta}) => soxiMeta.duration>=10;
}
