import {Format} from "../../Format.js";

export class windowsSCR extends Format
{
	name           = "Windows Screensaver";
	ext            = [".scr"];
	forbidExtMatch = true;
	magic          = ["Windows New Executable", "MS-DOS executable, NE for MS Windows 3.x", "Win16 NE executable", "Windows screen saver", /^fmt\/899( |$)/, /^x-fmt\/410( |$)/];
	weakMagic      = true;
	metaProvider   = ["winedump"];
	converters     = ["deark"];
	
	post = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}
