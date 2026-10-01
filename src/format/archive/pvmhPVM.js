import {Format} from "../../Format.js";

export class pvmhPVM extends Format
{
	name           = "PVMH PVM Archive";
	ext            = [".pvm"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PVM_PVMH( |$)/];
	converters     = ["gameextractor[codes:PVM_PVMH]"];
}
