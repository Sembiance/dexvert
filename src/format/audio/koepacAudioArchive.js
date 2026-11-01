import {Format} from "../../Format.js";

export class koepacAudioArchive extends Format
{
	name           = "Koepac audio archive";
	ext            = [".koe"];
	forbidExtMatch = true;
	magic          = ["Koepac audio archive", "RealLive Engine resource data", "archive:RealLive.KoeOpener"];
	converters     = ["vibe2wav", "GARbro[types:archive:RealLive.KoeOpener] -> sox[type:wav]"];
}
