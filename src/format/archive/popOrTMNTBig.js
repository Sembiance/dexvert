import {Format} from "../../Format.js";

export class popOrTMNTBig extends Format
{
	name           = "Prince of Persia Warrior Within or TMNT BIG Archive";
	ext            = [".big", ".fat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BIG( |$)/];
	auxFiles       = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.${input.ext.toLowerCase()===".big" ? "fat" : "big"}`);
	untouched      = ({f}) => f.input.ext.toLowerCase()===".fat";
	converters     = ["gameextractor[codes:BIG]"];
}
