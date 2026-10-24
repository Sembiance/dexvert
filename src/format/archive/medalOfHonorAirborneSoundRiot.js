import {Format} from "../../Format.js";

export class medalOfHonorAirborneSoundRiot extends Format
{
	name           = "Medal of Honor Airborne Sound Riot archive";
	ext            = [".soundriotrawasset"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SNB_SDPB( |$)/];
	converters     = ["gameextractor[codes:SNB_SDPB]"];
}
