import {Format} from "../../Format.js";

export class sid extends Format
{
	name         = "Commodore SID Music File";
	website      = "http://fileformats.archiveteam.org/wiki/SID";
	ext          = [".sid", ".psid", ".mus"];
	magic        = ["Play SID Audio", "PlaySID", "SID tune", "Real C64 SID tune", "RSID sidtune", "audio/prs.sid", /^fmt\/(314|315|316)( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="PSID" && macFileCreator==="SIDP";
	keepFilename = true;	// Needed to determine proper song length
	metaProvider = ["sidInfo"];
	converters   = dexState => ([[].pushSequence(1, (dexState.meta.sidSubSongCount || 1)).map(i => `sidplay2[songCount:${(dexState.meta.sidSubSongCount || 1)}][subSong:${i}][songLength:${(dexState.meta.sidSongLengths || [])[i-1] || "3:0"}]`).join(" & ")]);
}
