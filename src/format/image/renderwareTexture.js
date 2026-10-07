import {Format} from "../../Format.js";

export class renderwareTexture extends Format
{
	name       = "Renderware Texture";
	ext        = [".txd_tex"];
	magic      = [/^geViewer: TXD_2_TXDTEX( |$)/];
	converters = ["gameextractor[renameOut][codes:TXD_2_TXDTEX]"];
}
