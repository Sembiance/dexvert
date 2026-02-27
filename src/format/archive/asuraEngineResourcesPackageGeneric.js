import {Format} from "../../Format.js";

export class asuraEngineResourcesPackageGeneric extends Format
{
	name           = "Asura engine Resources package";
	ext            = [".asr"];
	forbidExtMatch = true;
	magic          = ["Asura engine Resources package", /^geArchive: ASR_ASURA_RSCF( |$)/, "dragon: Asura "];
	weakMagic      = true;
	converters     = ["gameextractor[codes:ASR_ASURA_RSCF]", "dragonUnpacker[types:Asura]"];
}
