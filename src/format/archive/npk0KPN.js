import {Format} from "../../Format.js";

export class npk0KPN extends Format
{
	name           = "NPK 0KPN Archive";
	ext            = [".npk"];
	forbidExtMatch = true;
	magic          = [/^geArchive: NPK_0KPN( |$)/];
	converters     = ["gameextractor[codes:NPK_0KPN]"];
}
