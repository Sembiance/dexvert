import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class renderwareTeXtureDictionary extends Format
{
	name           = "Renderware TeXture Dictionary";
	ext            = [".txd"];
	forbidExtMatch = true;
	magic          = ["Renderware TeXture Dictionary", "Renderware TeXture Dictionary (txd)", /^RenderWare data.*texture archive \(TXD\)/, /^geArchive: TXD_2( |$)/];
	metaProvider   = ["ffprobe[countFrames]"];
	keepFilename   = true;
	converters     = dexState => ["gameextractor[codes:TXD_2]", _FFMPEG_CONVERTERS_BUILDER({dexState, format : "txd", outType : "pngFrame"})];
}
