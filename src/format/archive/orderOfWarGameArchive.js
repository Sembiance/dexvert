import {Format} from "../../Format.js";

export class orderOfWarGameArchive extends Format
{
	name           = "Order of War Game Archive";
	ext            = [".pkg"];
	forbidExtMatch = true;
	magic          = ["Order of War game data archive", /^geArchive: PKG_PKGFILE( |$)/];
	converters     = ["gameextractor[codes:PKG_PKGFILE]"];
}
