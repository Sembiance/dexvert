import {Format} from "../../Format.js";

export class orionBurgerHAG extends Format
{
	name           = "Orion Burger HAG Archive";
	ext            = [".hag"];
	forbidExtMatch = true;
	magic          = [/^geArchive: HAG( |$)/];
	auxFiles       = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.has`);
	keepFilename   = true;
	converters     = ["gameextractor[codes:HAG]"];
}
