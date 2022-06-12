import {Format} from "../../Format.js";

export class calendarCreatorPlus extends Format
{
	name           = "Calendar Creator Plus Project";
	ext            = [".cce", ".bin"];
	forbidExtMatch = true;
	magic          = ["Calendar Creator Plus", /^x-fmt\/141( |$)/];
	converters     = ["strings"];
}
