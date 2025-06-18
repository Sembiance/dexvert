import {Format} from "../../Format.js";

const _VOB_MAGICS = ["Video OBject Datei - Teil einer DVD/VCD", "VOB video files", /^fmt\/425( |$)/];

export class mpeg2 extends Format
{
	name           = "MPEG-2";
	website        = "http://fileformats.archiveteam.org/wiki/MPEG-2";
	ext            = [".mpg", ".mp2", ".mpeg", ".m2v", ".m2ts", ".ts", ".vob", ".bin", ".mts"];
	forbidExtMatch = [".bin"];
	mimeType       = "video/mpeg";
	magic          = [
		// generic
		"MPEG-2 Elementary Stream", "MPEG-2 Program Stream", "MPEG sequence, v2", "MPEG-2 Transport Stream", "VideoCD MPEG", "video/mp2t",
		"MPEG-PS (MPEG-2 Program Stream) (mpeg)", "MPEG-TS (MPEG-2 Transport Stream) (mpegts)", /^MPEG transport stream data$/, "DVD Video Recording format",
		/^fmt\/(585|640|1055)( |$)/, /^x-fmt\/386( |$)/,
		..._VOB_MAGICS,

		// specific
		"PlayStation Portable Movie Format", "AVCHD video clips - MPEG Transport Stream", "BDAV MPEG-2 Transport Stream (M2TS)"
	];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="MPG2" || (macFileType==="MPEG" && macFileCreator==="TVOD");
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "xanim"];
	/*converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics(_VOB_MAGICS))
			r.push("handbrake");
		r.push("ffmpeg", "xanim");
		return r;
	};*/
}
