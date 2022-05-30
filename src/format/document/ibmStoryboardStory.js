import {Format} from "../../Format.js";

export class ibmStoryboardStory extends Format
{
	name           = "IBM Storyboard Story";
	ext            = [".sh", ".sh~"];
	forbidExtMatch = true;
	magic          = ["IBM Storyboard Story", "IBM PC Storyboard Story"];
	converters     = ["strings"];
}
