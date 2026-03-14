import {Format} from "../../Format.js";

export class whirlwindGameDataPackage extends Format
{
	name           = "Whirlwind game data Package";
	ext            = [".wpk"];
	forbidExtMatch = true;
	magic          = ["Whirlwind game data Package", /^geArchive: WPK( |$)/];
	converters     = ["gameextractor[codes:WPK]"];
}
