import {Format} from "../../Format.js";

export class renderwareTeXtureDictionary extends Format
{
	name           = "Renderware TeXture Dictionary";
	ext            = [".txd"];
	forbidExtMatch = true;
	magic          = ["Renderware TeXture Dictionary", /^RenderWare data.*texture archive \(TXD\)/, /^geArchive: TXD_2( |$)/];
	keepFilename   = true;
	converters     = ["gameextractor[codes:TXD_2]"];
}

