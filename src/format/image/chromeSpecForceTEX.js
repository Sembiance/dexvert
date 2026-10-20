import {Format} from "../../Format.js";

export class chromeSpecForceTEX extends Format
{
	name           = "Chrome SpecForce TEX";
	ext            = [".tex"];
	forbidExtMatch = true;
	magic          = [/^geViewer: TEX_ChromeSpecForce( |$)/];
	converters     = ["gameextractor[renameOut][codes:TEX_ChromeSpecForce]"];
}
