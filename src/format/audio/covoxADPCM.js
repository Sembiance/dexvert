import {Format} from "../../Format.js";

export class covoxADPCM extends Format
{
	name           = "Covox ADPCM Encoded Audio";
	website        = "https://wiki.multimedia.cx/index.php/Covox_ADPCM";
	ext            = [".v8", ".cvx"];
	forbidExtMatch = true;
	magic          = ["Covox ADPCM encoded audio", /^fmt\/1676( |$)/];
	converters     = ["awaveStudio"];
}
