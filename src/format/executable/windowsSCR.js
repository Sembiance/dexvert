import {Format} from "../../Format.js";
import {_WINDUMP_META_KEYS} from "../../program/meta/winedump.js";

export class windowsSCR extends Format
{
	name           = "Windows Screensaver";
	ext            = [".scr"];
	forbidExtMatch = true;
	magic          = ["Windows New Executable", "MS-DOS executable, NE for MS Windows 3.x", "Win16 NE executable", "Windows screen saver", /^fmt\/899( |$)/, /^x-fmt\/410( |$)/];
	weakMagic      = true;
	metaProvider   = ["winedump", "exiftool"];
	converters     = ["deark[module:exe]"];
	notes          = "Could be fun to 'run' these in Wine and record the output into a preview.mp4 video";
	
	post = dexState =>
	{
		if(Object.keys(dexState.meta).includesAny(_WINDUMP_META_KEYS))
			dexState.processed = true;
	};
}
