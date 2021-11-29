import {Format} from "../../Format.js";

export class microsoftChatCharacter extends Format
{
	name        = "Microsoft Comic Chat Character";
	website     = "http://fileformats.archiveteam.org/wiki/Microsoft_Comic_Chat";
	ext         = [".avb"];
	magic       = ["Microsoft Chat Character"];
	unsupported = true;
}
