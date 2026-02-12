import {Format} from "../../Format.js";

export class xcrArchive extends Format
{
	name           = "XCR archive";
	ext            = [".xcr"];
	forbidExtMatch = true;
	magic          = ["XCR archive", "Format: XCR", /^geArchive: XCR_XCR( |$)/];
	converters     = ["gameextractor[codes:XCR_XCR]"];
}
