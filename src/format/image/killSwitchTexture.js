import {Format} from "../../Format.js";

export class killSwitchTexture extends Format
{
	name       = "Kill Switch Texture";
	ext        = [".txd_tex"];
	magic      = [/^geViewer: TXD_2_TXDTEX( |$)/];
	converters = ["gameextractor[renameOut][codes:TXD_2_TXDTEX]"];
}
