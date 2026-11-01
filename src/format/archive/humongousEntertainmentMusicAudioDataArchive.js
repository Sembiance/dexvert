import {Format} from "../../Format.js";

export class humongousEntertainmentMusicAudioDataArchive extends Format
{
	name           = "Humongous Entertainment music/audio data archive";
	ext            = [".he4"];
	forbidExtMatch = true;
	magic          = ["Humongous Entertainment music/audio data archive", /^geArchive: HE4_SONG( |$)/];
	converters     = ["gameextractor[codes:HE4_SONG]"];
}
