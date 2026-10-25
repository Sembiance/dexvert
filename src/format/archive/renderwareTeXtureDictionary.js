import {Format} from "../../Format.js";

export class renderwareTeXtureDictionary extends Format
{
	name           = "Renderware TeXture Dictionary";
	ext            = [".txd"];
	forbidExtMatch = true;
	magic          = ["Renderware TeXture Dictionary", "Renderware TeXture Dictionary (txd)", /^RenderWare data.*texture archive \(TXD\)/, /^geArchive: TXD_2( |$)/];
	keepFilename   = true;
	converters     = ["gameextractor[codes:TXD_2]"];
}
